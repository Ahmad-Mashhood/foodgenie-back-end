from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, delete, or_, and_
from database import AsyncSessionLocal, serialize_doc
from models.food_model import FoodCreate, FoodUpdate
from orm_models import Food, Vendor

async def get_all_foods():
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(select(Food).where(Food.is_available == True))
            foods = res.scalars().all()
            
            serialized_foods = serialize_doc(list(foods))
            for food in serialized_foods:
                v_id = food.get("vendor_id")
                if v_id:
                    v_res = await session.execute(select(Vendor).where(Vendor.id == str(v_id)))
                    v_doc = v_res.scalar_one_or_none()
                    if v_doc:
                        v_clean = serialize_doc(v_doc)
                        v_clean.pop("password", None)
                        food["vendor"] = v_clean
            return serialized_foods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch foods: {str(e)}"
        )

async def get_food_by_id(food_id: str):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Food).where(Food.id == str(food_id)))
        food = res.scalar_one_or_none()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

        serialized = serialize_doc(food)
        v_id = serialized.get("vendor_id")
        if v_id:
            v_res = await session.execute(select(Vendor).where(Vendor.id == str(v_id)))
            vendor = v_res.scalar_one_or_none()
            if vendor:
                v_clean = serialize_doc(vendor)
                v_clean.pop("password", None)
                serialized["vendor"] = v_clean

        return serialized

async def get_foods_by_category(category: str):
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(
                select(Food).where(
                    and_(
                        Food.category.ilike(category),
                        Food.is_available == True
                    )
                )
            )
            foods = res.scalars().all()
            return serialize_doc(list(foods))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch foods by category: {str(e)}"
        )

async def filter_foods(category: Optional[str] = None, calories: Optional[int] = None, city: Optional[str] = None):
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(Food).where(Food.is_available == True)

            if calories is not None:
                stmt = stmt.where(Food.calories <= calories)

            if category:
                stmt = stmt.where(Food.category.ilike(f"%{category}%"))

            if city:
                v_res = await session.execute(
                    select(Vendor.id).where(
                        and_(
                            Vendor.address.ilike(f"%{city}%"),
                            Vendor.is_active == True
                        )
                    )
                )
                vendor_ids = [v[0] for v in v_res.all()]
                stmt = stmt.where(Food.vendor_id.in_(vendor_ids))

            res = await session.execute(stmt)
            foods = res.scalars().all()
            serialized_foods = serialize_doc(list(foods))

            for food in serialized_foods:
                v_id = food.get("vendor_id")
                if v_id:
                    v_res = await session.execute(select(Vendor).where(Vendor.id == str(v_id)))
                    v_doc = v_res.scalar_one_or_none()
                    if v_doc:
                        food["vendor"] = serialize_doc(v_doc)

            return serialized_foods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Filter failed: {str(e)}"
        )

async def create_food(data: FoodCreate, current_user: dict):
    try:
        vendor_id_str = data.vendorId or current_user["id"]

        async with AsyncSessionLocal() as session:
            food_obj = Food(
                vendor_id=str(vendor_id_str),
                name=data.name,
                price=data.price,
                category=data.category,
                description=data.description,
                calories=data.calories or 0,
                is_available=data.isAvailable,
                tags=data.tags or [],
                image=data.image
            )

            session.add(food_obj)
            await session.commit()
            await session.refresh(food_obj)
            return serialize_doc(food_obj)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create food item: {str(e)}"
        )

async def update_food(food_id: str, data: FoodUpdate, current_user: dict):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Food).where(Food.id == str(food_id)))
        food = res.scalar_one_or_none()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

        if current_user.get("role") == "vendor":
            if str(food.vendor_id) != str(current_user["id"]):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to edit this food item")

        update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
        for k, v in update_dict.items():
            if k == "isAvailable":
                food.is_available = v
            elif hasattr(food, k):
                setattr(food, k, v)

        await session.commit()
        await session.refresh(food)
        return serialize_doc(food)

async def delete_food(food_id: str, current_user: dict):
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Food).where(Food.id == str(food_id)))
        food = res.scalar_one_or_none()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

        if current_user.get("role") == "vendor":
            if str(food.vendor_id) != str(current_user["id"]):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete this food item")

        await session.delete(food)
        await session.commit()
        return {"message": "Food item deleted successfully"}

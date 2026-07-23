from typing import Optional
from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from schemas.food import FoodCreate, FoodUpdate
from models.food import Food
from models.vendor import Vendor

async def get_all_foods():
    session = SyncSessionLocal()
    try:
        foods = session.query(Food).filter(Food.is_available == True).all()
        serialized_foods = serialize_doc(foods)
        for food in serialized_foods:
            if food.get("vendor_id"):
                v_doc = session.query(Vendor).filter(Vendor.id == food["vendor_id"]).first()
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
    finally:
        session.close()

async def get_food_by_id(food_id: int):
    session = SyncSessionLocal()
    try:
        food = session.query(Food).filter(Food.id == food_id).first()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

        serialized = serialize_doc(food)
        if serialized.get("vendor_id"):
            vendor = session.query(Vendor).filter(Vendor.id == serialized["vendor_id"]).first()
            if vendor:
                v_clean = serialize_doc(vendor)
                v_clean.pop("password", None)
                serialized["vendor"] = v_clean

        return serialized
    finally:
        session.close()

async def get_foods_by_category(category: str):
    session = SyncSessionLocal()
    try:
        foods = session.query(Food).filter(
            Food.category.ilike(category),
            Food.is_available == True
        ).all()
        return serialize_doc(foods)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch foods by category: {str(e)}"
        )
    finally:
        session.close()

async def filter_foods(
    category: Optional[str] = None,
    max_calories: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    is_available: Optional[bool] = None,
    vendor_id: Optional[int] = None
):
    session = SyncSessionLocal()
    try:
        query = session.query(Food)

        if is_available is not None:
            query = query.filter(Food.is_available == is_available)

        if category:
            query = query.filter(Food.category.ilike(f"%{category}%"))

        if max_calories is not None:
            query = query.filter(Food.calories <= max_calories)

        if min_price is not None:
            query = query.filter(Food.price >= min_price)

        if max_price is not None:
            query = query.filter(Food.price <= max_price)

        if vendor_id is not None:
            query = query.filter(Food.vendor_id == vendor_id)

        foods = query.all()
        serialized_foods = serialize_doc(foods)

        for food in serialized_foods:
            if food.get("vendor_id"):
                v_doc = session.query(Vendor).filter(Vendor.id == food["vendor_id"]).first()
                if v_doc:
                    v_clean = serialize_doc(v_doc)
                    v_clean.pop("password", None)
                    food["vendor"] = v_clean

        return serialized_foods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Filter failed: {str(e)}"
        )
    finally:
        session.close()

async def create_food(data: FoodCreate, current_user: dict):
    session = SyncSessionLocal()
    try:
        v_id = data.vendor_id or current_user.get("id")
        
        food_obj = Food(
            name=data.name,
            price=data.price,
            category=data.category,
            description=data.description,
            calories=data.calories or 0,
            is_available=data.is_available,
            vendor_id=v_id
        )

        session.add(food_obj)
        session.commit()
        session.refresh(food_obj)

        return serialize_doc(food_obj)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create food item: {str(e)}"
        )
    finally:
        session.close()

async def update_food(food_id: int, data: FoodUpdate, current_user: dict):
    session = SyncSessionLocal()
    try:
        food = session.query(Food).filter(Food.id == food_id).first()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

        if current_user.get("role") == "vendor" and food.vendor_id != current_user.get("id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to edit this food item")

        update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
        for k, v in update_dict.items():
            if hasattr(food, k):
                setattr(food, k, v)

        session.commit()
        session.refresh(food)
        return serialize_doc(food)
    finally:
        session.close()

async def delete_food(food_id: int, current_user: dict):
    session = SyncSessionLocal()
    try:
        food = session.query(Food).filter(Food.id == food_id).first()
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

        if current_user.get("role") == "vendor" and food.vendor_id != current_user.get("id"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete this food item")

        session.delete(food)
        session.commit()
        return {"message": "Food item deleted successfully"}
    finally:
        session.close()

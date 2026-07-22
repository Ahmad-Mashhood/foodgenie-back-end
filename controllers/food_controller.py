import re
from typing import Optional
from fastapi import HTTPException, status
from database import db, parse_object_id, serialize_doc
from models.food_model import FoodCreate, FoodUpdate

async def get_all_foods():
    try:
        cursor = db.menuitems.find({"isAvailable": True})
        foods = await cursor.to_list(length=500)
        
        serialized_foods = serialize_doc(foods)
        # Populate vendor info
        for food in serialized_foods:
            if food.get("vendor"):
                v_id = parse_object_id(food["vendor"])
                if v_id:
                    v_doc = await db.vendors.find_one({"_id": v_id})
                    if v_doc:
                        v_clean = serialize_doc(v_doc)
                        v_clean.pop("password", None)
                        food["vendor"] = v_clean
            elif food.get("vendorId"):
                v_id = parse_object_id(food["vendorId"])
                if v_id:
                    v_doc = await db.vendors.find_one({"_id": v_id})
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
    obj_id = parse_object_id(food_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Food ID")

    food = await db.menuitems.find_one({"_id": obj_id})
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    serialized = serialize_doc(food)
    
    # Populate vendor
    v_raw_id = serialized.get("vendor") or serialized.get("vendorId")
    if v_raw_id:
        v_id = parse_object_id(str(v_raw_id))
        if v_id:
            vendor = await db.vendors.find_one({"_id": v_id})
            if vendor:
                v_clean = serialize_doc(vendor)
                v_clean.pop("password", None)
                serialized["vendor"] = v_clean

    return serialized

async def get_foods_by_category(category: str):
    try:
        regex = re.compile(f"^{re.escape(category)}$", re.IGNORECASE)
        cursor = db.menuitems.find({"category": regex, "isAvailable": True})
        foods = await cursor.to_list(length=200)
        return serialize_doc(foods)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch foods by category: {str(e)}"
        )

async def filter_foods(category: Optional[str] = None, calories: Optional[int] = None, city: Optional[str] = None):
    try:
        query = {"isAvailable": True}

        if calories is not None:
            query["calories"] = {"$lte": calories}

        if category:
            cat_regex = re.compile(re.escape(category), re.IGNORECASE)
            query["$or"] = [
                {"category": cat_regex},
                {"tags": {"$in": [category.lower()]}}
            ]

        if city:
            city_regex = re.compile(re.escape(city), re.IGNORECASE)
            vendors_in_city = await db.vendors.find({"address": city_regex, "isActive": True}).to_list(length=100)
            vendor_ids = [v["_id"] for v in vendors_in_city]
            query["vendor"] = {"$in": vendor_ids}

        cursor = db.menuitems.find(query)
        foods = await cursor.to_list(length=200)
        serialized_foods = serialize_doc(foods)

        for food in serialized_foods:
            v_raw = food.get("vendor") or food.get("vendorId")
            if v_raw:
                v_id = parse_object_id(str(v_raw))
                if v_id:
                    v_doc = await db.vendors.find_one({"_id": v_id})
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
        v_obj_id = parse_object_id(vendor_id_str)

        food_doc = {
            "vendor": v_obj_id if v_obj_id else vendor_id_str,
            "vendorId": str(vendor_id_str),
            "name": data.name,
            "price": data.price,
            "category": data.category,
            "description": data.description,
            "calories": data.calories,
            "isAvailable": data.isAvailable,
            "tags": data.tags,
            "image": data.image
        }

        result = await db.menuitems.insert_one(food_doc)
        food_doc["_id"] = result.inserted_id
        return serialize_doc(food_doc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create food item: {str(e)}"
        )

async def update_food(food_id: str, data: FoodUpdate, current_user: dict):
    obj_id = parse_object_id(food_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Food ID")

    food = await db.menuitems.find_one({"_id": obj_id})
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    # Check vendor ownership if role is vendor
    if current_user.get("role") == "vendor":
        v_id_str = str(food.get("vendor") or food.get("vendorId") or "")
        if v_id_str != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to edit this food item")

    update_dict = {k: v for k, v in data.dict(exclude_unset=True).items() if v is not None}
    if not update_dict:
        return serialize_doc(food)

    await db.menuitems.update_one({"_id": obj_id}, {"$set": update_dict})
    updated_food = await db.menuitems.find_one({"_id": obj_id})
    return serialize_doc(updated_food)

async def delete_food(food_id: str, current_user: dict):
    obj_id = parse_object_id(food_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Food ID")

    food = await db.menuitems.find_one({"_id": obj_id})
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food item not found")

    if current_user.get("role") == "vendor":
        v_id_str = str(food.get("vendor") or food.get("vendorId") or "")
        if v_id_str != current_user["id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized to delete this food item")

    await db.menuitems.delete_one({"_id": obj_id})
    return {"message": "Food item deleted successfully"}

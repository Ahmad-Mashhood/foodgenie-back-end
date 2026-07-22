import re
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import HTTPException, status
from database import db, parse_object_id, serialize_doc

class RecommendationCriteria(BaseModel):
    diet: Optional[str] = Field(None, example="vegan")
    calories: Optional[int] = Field(None, example=600)
    healthGoals: Optional[List[str]] = Field(None, example=["low-fat", "healthy"])
    allergies: Optional[List[str]] = Field(None, example=["nuts"])

async def get_recommendations_for_customer(customer_id: str, current_user: dict):
    obj_id = parse_object_id(customer_id)
    if not obj_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Customer ID")

    customer = await db.users.find_one({"_id": obj_id})
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    prefs = customer.get("preferences") or {}
    query = {"isAvailable": True}

    if prefs.get("calories"):
        query["calories"] = {"$lte": int(prefs["calories"])}

    target_tags = []
    if prefs.get("diet"):
        target_tags.append(prefs["diet"].lower())
    if prefs.get("healthGoals"):
        for goal in prefs["healthGoals"]:
            target_tags.append(goal.lower())

    if target_tags:
        query["tags"] = {"$in": target_tags}

    cursor = db.menuitems.find(query).limit(10)
    recommendations = await cursor.to_list(length=10)

    # Fallback to general foods if no exact match
    if not recommendations:
        cursor = db.menuitems.find({"isAvailable": True}).limit(10)
        recommendations = await cursor.to_list(length=10)

    serialized = serialize_doc(recommendations)

    # Populate vendors
    for food in serialized:
        v_raw = food.get("vendor") or food.get("vendorId")
        if v_raw:
            v_id = parse_object_id(str(v_raw))
            if v_id:
                vendor = await db.vendors.find_one({"_id": v_id})
                if vendor:
                    food["vendor"] = serialize_doc(vendor)

    return serialized

async def generate_recommendations(data: RecommendationCriteria, current_user: dict):
    try:
        query = {"isAvailable": True}

        if data.calories is not None:
            query["calories"] = {"$lte": data.calories}

        target_tags = []
        if data.diet:
            target_tags.append(data.diet.lower())
        if data.healthGoals:
            for g in data.healthGoals:
                target_tags.append(g.lower())

        if target_tags:
            query["tags"] = {"$in": target_tags}

        cursor = db.menuitems.find(query).limit(10)
        recommendations = await cursor.to_list(length=10)

        serialized = serialize_doc(recommendations)
        for food in serialized:
            v_raw = food.get("vendor") or food.get("vendorId")
            if v_raw:
                v_id = parse_object_id(str(v_raw))
                if v_id:
                    vendor = await db.vendors.find_one({"_id": v_id})
                    if vendor:
                        food["vendor"] = serialize_doc(vendor)

        return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

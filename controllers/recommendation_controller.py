import re
from typing import Optional, List
from pydantic import BaseModel, Field
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from database import AsyncSessionLocal, serialize_doc
from orm_models import User, Food, Vendor

class RecommendationCriteria(BaseModel):
    diet: Optional[str] = Field(None, example="vegan")
    calories: Optional[int] = Field(None, example=600)
    healthGoals: Optional[List[str]] = Field(None, example=["low-fat", "healthy"])
    allergies: Optional[List[str]] = Field(None, example=["nuts"])

async def get_recommendations_for_customer(customer_id: str, current_user: dict):
    async with AsyncSessionLocal() as session:
        c_res = await session.execute(select(User).where(User.id == str(customer_id)))
        customer = c_res.scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        prefs = customer.preferences or {}
        stmt = select(Food).where(Food.is_available == True)

        if prefs.get("calories"):
            stmt = stmt.where(Food.calories <= int(prefs["calories"]))

        stmt = stmt.limit(10)
        res = await session.execute(stmt)
        recommendations = res.scalars().all()

        if not recommendations:
            res_all = await session.execute(select(Food).where(Food.is_available == True).limit(10))
            recommendations = res_all.scalars().all()

        serialized = serialize_doc(list(recommendations))

        for food in serialized:
            v_id = food.get("vendor_id")
            if v_id:
                v_res = await session.execute(select(Vendor).where(Vendor.id == str(v_id)))
                vendor = v_res.scalar_one_or_none()
                if vendor:
                    v_clean = serialize_doc(vendor)
                    v_clean.pop("password", None)
                    food["vendor"] = v_clean

        return serialized

async def generate_recommendations(data: RecommendationCriteria, current_user: dict):
    try:
        async with AsyncSessionLocal() as session:
            stmt = select(Food).where(Food.is_available == True)

            if data.calories is not None:
                stmt = stmt.where(Food.calories <= data.calories)

            stmt = stmt.limit(10)
            res = await session.execute(stmt)
            recommendations = res.scalars().all()

            serialized = serialize_doc(list(recommendations))
            for food in serialized:
                v_id = food.get("vendor_id")
                if v_id:
                    v_res = await session.execute(select(Vendor).where(Vendor.id == str(v_id)))
                    vendor = v_res.scalar_one_or_none()
                    if vendor:
                        v_clean = serialize_doc(vendor)
                        v_clean.pop("password", None)
                        food["vendor"] = v_clean

            return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

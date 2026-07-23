from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from schemas.review import RecommendationCriteria
from models.user import User
from models.user_preferences import UserPreferences
from models.food import Food
from models.vendor import Vendor

async def get_recommendations_for_customer(customer_id: int, current_user: dict):
    session = SyncSessionLocal()
    try:
        customer = session.query(User).filter(User.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

        prefs = session.query(UserPreferences).filter(UserPreferences.user_id == customer_id).first()
        query = session.query(Food).filter(Food.is_available == True)

        if prefs:
            if prefs.max_calories:
                query = query.filter(Food.calories <= prefs.max_calories)
            if prefs.diet_type and prefs.diet_type != "any":
                query = query.filter(Food.category.ilike(f"%{prefs.diet_type}%"))

        recommendations = query.limit(10).all()
        if not recommendations:
            recommendations = session.query(Food).filter(Food.is_available == True).limit(10).all()

        serialized = serialize_doc(recommendations)
        for food in serialized:
            if food.get("vendor_id"):
                v_doc = session.query(Vendor).filter(Vendor.id == food["vendor_id"]).first()
                if v_doc:
                    v_clean = serialize_doc(v_doc)
                    v_clean.pop("password", None)
                    food["vendor"] = v_clean

        return serialized
    finally:
        session.close()

async def generate_recommendations(data: RecommendationCriteria, current_user: dict):
    session = SyncSessionLocal()
    try:
        query = session.query(Food).filter(Food.is_available == True)

        if data.max_calories is not None:
            query = query.filter(Food.calories <= data.max_calories)

        if data.diet_type and data.diet_type != "any":
            query = query.filter(Food.category.ilike(f"%{data.diet_type}%"))

        if data.preferred_cuisine:
            query = query.filter(Food.category.ilike(f"%{data.preferred_cuisine}%"))

        recommendations = query.limit(10).all()
        if not recommendations:
            recommendations = session.query(Food).filter(Food.is_available == True).limit(10).all()

        serialized = serialize_doc(recommendations)
        for food in serialized:
            if food.get("vendor_id"):
                v_doc = session.query(Vendor).filter(Vendor.id == food["vendor_id"]).first()
                if v_doc:
                    v_clean = serialize_doc(v_doc)
                    v_clean.pop("password", None)
                    food["vendor"] = v_clean

        return serialized
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )
    finally:
        session.close()

from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import require_roles
from schemas.food import FoodResponse
from schemas.review import RecommendationCriteria
from controllers import recommendation_controller

router = APIRouter(prefix="/api/recommendations", tags=["Smart Health Recommendations"])

@router.get(
    "/{customer_id}",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Recommendations for Customer (Customer Only)",
    description="Returns food recommendations based on customer dietary preferences and calories."
)
async def get_recommendations_for_customer(
    customer_id: int,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await recommendation_controller.get_recommendations_for_customer(customer_id, current_user)

@router.post(
    "/generate",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate Custom Health Recommendations (Customer Only)",
    description="Generates tailored food recommendations for given criteria (diet_type, max_calories, allergies, preferred_cuisine)."
)
async def generate_recommendations(
    data: RecommendationCriteria,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await recommendation_controller.generate_recommendations(data, current_user)

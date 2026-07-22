from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth import require_roles
from models.food_model import FoodResponse
from controllers import recommendation_controller
from controllers.recommendation_controller import RecommendationCriteria

router = APIRouter(prefix="/api/recommendations", tags=["Smart Health Recommendations"])

@router.get(
    "/{customer_id}",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Health Recommendations for Customer (Customer Only)",
    description="Returns AI/Rule-based food recommendations matched to the stored customer health preferences."
)
async def get_recommendations_for_customer(
    customer_id: str,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await recommendation_controller.get_recommendations_for_customer(customer_id, current_user)

@router.post(
    "/generate",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Generate On-Demand Health Recommendations (Customer Only)",
    description="Generates food recommendations based on on-the-fly request criteria (diet, calories limit, health goals)."
)
async def generate_recommendations(
    data: RecommendationCriteria,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await recommendation_controller.generate_recommendations(data, current_user)

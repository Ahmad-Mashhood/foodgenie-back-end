from typing import List
from fastapi import APIRouter, Depends, status
from middleware.auth_middleware import require_roles
from schemas.review import ReviewCreate, ReviewResponse
from controllers import review_controller

router = APIRouter(prefix="/api/reviews", tags=["Reviews & Ratings"])

@router.post(
    "",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Vendor/Food Review (Customer Only)",
    description="Submits a review and rating for a vendor or food item."
)
async def create_review(
    data: ReviewCreate,
    current_user: dict = Depends(require_roles(["customer", "admin"]))
):
    return await review_controller.create_review(data, current_user)

@router.get(
    "/vendor/{vendor_id}",
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Vendor Reviews (Public)",
    description="Returns all customer reviews for the specified vendor."
)
async def get_vendor_reviews(vendor_id: int):
    return await review_controller.get_vendor_reviews(vendor_id)

@router.get(
    "/food/{food_id}",
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Food Item Reviews (Public)",
    description="Returns all customer reviews for the specified food item."
)
async def get_food_reviews(food_id: int):
    return await review_controller.get_food_reviews(food_id)

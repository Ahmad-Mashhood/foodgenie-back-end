from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from middleware.auth_middleware import require_roles
from schemas.food import FoodCreate, FoodUpdate, FoodResponse
from controllers import food_controller

router = APIRouter(prefix="/api/foods", tags=["Food Items & Menu"])

@router.get(
    "",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Available Foods",
    description="Returns list of all available food items with vendor info."
)
async def get_all_foods():
    return await food_controller.get_all_foods()

@router.get(
    "/filter",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Filter Foods by Query Criteria",
    description="Filters foods by category, max_calories, min_price, max_price, is_available, or vendor_id."
)
async def filter_foods(
    category: Optional[str] = Query(None, description="Category name filter"),
    max_calories: Optional[int] = Query(None, description="Maximum calories filter"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    is_available: Optional[bool] = Query(None, description="Availability status filter"),
    vendor_id: Optional[int] = Query(None, description="Vendor ID filter")
):
    return await food_controller.filter_foods(category, max_calories, min_price, max_price, is_available, vendor_id)

@router.get(
    "/category/{category}",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Foods by Category",
    description="Returns foods matching the specified category."
)
async def get_foods_by_category(category: str):
    return await food_controller.get_foods_by_category(category)

@router.get(
    "/{food_id}",
    response_model=FoodResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Food Item Details",
    description="Returns details for a single food item."
)
async def get_food_by_id(food_id: int):
    return await food_controller.get_food_by_id(food_id)

@router.post(
    "",
    response_model=FoodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Food Item (Vendor/Admin)",
    description="Creates a new food item in the vendor menu."
)
async def create_food(
    data: FoodCreate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await food_controller.create_food(data, current_user)

@router.put(
    "/{food_id}",
    response_model=FoodResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Food Item (Vendor/Admin)",
    description="Updates existing food item fields."
)
async def update_food(
    food_id: int,
    data: FoodUpdate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await food_controller.update_food(food_id, data, current_user)

@router.delete(
    "/{food_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Food Item (Vendor/Admin)",
    description="Removes a food item from the database."
)
async def delete_food(
    food_id: int,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await food_controller.delete_food(food_id, current_user)

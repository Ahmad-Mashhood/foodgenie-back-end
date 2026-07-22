from typing import Optional, List
from fastapi import APIRouter, Depends, Query, status
from middleware.auth import require_roles
from models.food_model import FoodCreate, FoodUpdate, FoodResponse
from controllers import food_controller

router = APIRouter(prefix="/api/foods", tags=["Food Items & Menu"])

@router.get(
    "",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get All Food Items",
    description="Public endpoint to list all available food items along with populated vendor details."
)
async def get_all_foods():
    return await food_controller.get_all_foods()

@router.get(
    "/filter",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Filter Food Items",
    description="Filters foods by category, max calories limit, or vendor location city."
)
async def filter_foods(
    category: Optional[str] = Query(None, description="Category or tag filter e.g. healthy, biryani"),
    calories: Optional[int] = Query(None, description="Maximum calories limit e.g. 500"),
    city: Optional[str] = Query(None, description="City location e.g. Vehari")
):
    return await food_controller.filter_foods(category=category, calories=calories, city=city)

@router.get(
    "/{food_id}",
    response_model=FoodResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Single Food Item",
    description="Fetches food item details by unique item ID."
)
async def get_food_by_id(food_id: str):
    return await food_controller.get_food_by_id(food_id)

@router.get(
    "/category/{category}",
    response_model=List[FoodResponse],
    status_code=status.HTTP_200_OK,
    summary="Get Foods by Category",
    description="Fetches food items matching a specific food category e.g. biryani, healthy, fastfood."
)
async def get_foods_by_category(category: str):
    return await food_controller.get_foods_by_category(category)

@router.post(
    "",
    response_model=FoodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Food Item (Vendor/Admin Only)",
    description="Adds a new food item to a vendor's menu."
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
    summary="Update Food Item (Vendor/Admin Only)",
    description="Updates attributes of an existing food item."
)
async def update_food(
    food_id: str,
    data: FoodUpdate,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await food_controller.update_food(food_id, data, current_user)

@router.delete(
    "/{food_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete Food Item (Vendor/Admin Only)",
    description="Removes a food item from the menu catalog."
)
async def delete_food(
    food_id: str,
    current_user: dict = Depends(require_roles(["vendor", "admin"]))
):
    return await food_controller.delete_food(food_id, current_user)

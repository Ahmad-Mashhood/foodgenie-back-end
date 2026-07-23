from fastapi import APIRouter, Query, status
from controllers import search_controller

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Search Foods and Vendors (Public)",
    description="Performs keyword search matching foods and local vendors."
)
async def search(q: str = Query(..., description="Keyword search string")):
    return await search_controller.search_query(q)

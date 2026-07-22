from fastapi import APIRouter, Query, status
from controllers import search_controller

router = APIRouter(prefix="/api/search", tags=["Search"])

@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Global Keyword Search",
    description="Public multi-resource search querying food names, descriptions, categories, vendor names, and cuisines."
)
async def search(
    q: str = Query(..., example="biryani", description="Search keyword query parameter")
):
    return await search_controller.search_query(q)

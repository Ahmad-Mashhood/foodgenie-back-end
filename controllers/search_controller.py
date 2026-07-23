from fastapi import HTTPException, status
from sqlalchemy import select, or_, and_
from database import AsyncSessionLocal, serialize_doc
from orm_models import Vendor, Food

async def search_query(q: str):
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query parameter 'q' is required"
        )

    try:
        async with AsyncSessionLocal() as session:
            pattern = f"%{q}%"

            # 1. Search Vendors
            v_res = await session.execute(
                select(Vendor).where(
                    and_(
                        Vendor.is_active == True,
                        or_(
                            Vendor.name.ilike(pattern),
                            Vendor.cuisine.ilike(pattern),
                            Vendor.category.ilike(pattern),
                            Vendor.address.ilike(pattern),
                            Vendor.city.ilike(pattern)
                        )
                    )
                ).limit(50)
            )
            vendors = v_res.scalars().all()

            # 2. Search Foods
            f_res = await session.execute(
                select(Food).where(
                    and_(
                        Food.is_available == True,
                        or_(
                            Food.name.ilike(pattern),
                            Food.description.ilike(pattern),
                            Food.category.ilike(pattern)
                        )
                    )
                ).limit(50)
            )
            foods = f_res.scalars().all()

            serialized_vendors = serialize_doc(list(vendors))
            for v in serialized_vendors:
                v.pop("password", None)

            serialized_foods = serialize_doc(list(foods))
            for food in serialized_foods:
                v_id = food.get("vendor_id")
                if v_id:
                    v_doc_res = await session.execute(select(Vendor).where(Vendor.id == str(v_id)))
                    v_doc = v_doc_res.scalar_one_or_none()
                    if v_doc:
                        v_clean = serialize_doc(v_doc)
                        v_clean.pop("password", None)
                        food["vendor"] = v_clean

            return {
                "query": q,
                "vendors": serialized_vendors,
                "foods": serialized_foods
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

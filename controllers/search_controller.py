from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from models.vendor import Vendor
from models.food import Food

async def search_query(q: str):
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query parameter 'q' is required"
        )

    session = SyncSessionLocal()
    try:
        pattern = f"%{q}%"

        # Search Vendors
        vendors = session.query(Vendor).filter(
            Vendor.is_approved == True,
            (Vendor.name.ilike(pattern) | Vendor.category.ilike(pattern) | Vendor.city.ilike(pattern))
        ).limit(50).all()

        # Search Foods
        foods = session.query(Food).filter(
            Food.is_available == True,
            (Food.name.ilike(pattern) | Food.description.ilike(pattern) | Food.category.ilike(pattern))
        ).limit(50).all()

        serialized_vendors = serialize_doc(vendors)
        for v in serialized_vendors:
            v.pop("password", None)

        serialized_foods = serialize_doc(foods)
        for food in serialized_foods:
            if food.get("vendor_id"):
                v_doc = session.query(Vendor).filter(Vendor.id == food["vendor_id"]).first()
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
    finally:
        session.close()

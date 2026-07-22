import re
from fastapi import HTTPException, status
from database import db, serialize_doc, parse_object_id

async def search_query(q: str):
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query parameter 'q' is required"
        )

    try:
        regex = re.compile(re.escape(q), re.IGNORECASE)

        # 1. Search Vendors
        vendor_cursor = db.vendors.find({
            "isActive": True,
            "$or": [
                {"name": regex},
                {"cuisine": regex},
                {"category": regex},
                {"address": regex},
                {"city": regex}
            ]
        })
        vendors = await vendor_cursor.to_list(length=50)

        # 2. Search Foods
        food_cursor = db.menuitems.find({
            "isAvailable": True,
            "$or": [
                {"name": regex},
                {"description": regex},
                {"category": regex},
                {"tags": {"$in": [q.lower()]}}
            ]
        })
        foods = await food_cursor.to_list(length=50)

        serialized_vendors = serialize_doc(vendors)
        for v in serialized_vendors:
            v.pop("password", None)

        serialized_foods = serialize_doc(foods)
        for food in serialized_foods:
            v_raw = food.get("vendor") or food.get("vendorId")
            if v_raw:
                v_id = parse_object_id(str(v_raw))
                if v_id:
                    v_doc = await db.vendors.find_one({"_id": v_id})
                    if v_doc:
                        food["vendor"] = serialize_doc(v_doc)

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

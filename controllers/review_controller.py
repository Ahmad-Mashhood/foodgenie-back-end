from fastapi import HTTPException, status
from database import SyncSessionLocal, serialize_doc
from schemas.review import ReviewCreate
from models.review import Review
from models.vendor import Vendor
from models.user import User

async def create_review(data: ReviewCreate, current_user: dict):
    session = SyncSessionLocal()
    try:
        user_id = current_user["id"]
        review_obj = Review(
            user_id=user_id,
            vendor_id=data.vendor_id,
            food_id=data.food_id,
            rating=data.rating,
            comment=data.comment
        )
        session.add(review_obj)
        session.commit()
        session.refresh(review_obj)

        # Recalculate Vendor Average Rating
        avg_rating = session.query(Review.rating).filter(Review.vendor_id == data.vendor_id).all()
        if avg_rating:
            ratings = [r[0] for r in avg_rating if r[0] is not None]
            if ratings:
                new_avg = round(sum(ratings) / len(ratings), 1)
                vendor = session.query(Vendor).filter(Vendor.id == data.vendor_id).first()
                if vendor:
                    vendor.rating = new_avg
                    session.commit()

        return serialize_doc(review_obj)
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Review submission failed: {str(e)}"
        )
    finally:
        session.close()

async def get_vendor_reviews(vendor_id: int):
    session = SyncSessionLocal()
    try:
        reviews = session.query(Review).filter(Review.vendor_id == vendor_id).order_by(Review.created_at.desc()).all()
        serialized = serialize_doc(reviews)
        for r in serialized:
            if r.get("user_id"):
                u_doc = session.query(User).filter(User.id == r["user_id"]).first()
                if u_doc:
                    r["user_name"] = u_doc.name
        return serialized
    finally:
        session.close()

async def get_food_reviews(food_id: int):
    session = SyncSessionLocal()
    try:
        reviews = session.query(Review).filter(Review.food_id == food_id).order_by(Review.created_at.desc()).all()
        serialized = serialize_doc(reviews)
        for r in serialized:
            if r.get("user_id"):
                u_doc = session.query(User).filter(User.id == r["user_id"]).first()
                if u_doc:
                    r["user_name"] = u_doc.name
        return serialized
    finally:
        session.close()

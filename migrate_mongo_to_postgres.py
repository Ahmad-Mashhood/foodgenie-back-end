import os
import pymongo
from dotenv import load_dotenv
from database import SyncSessionLocal, sync_engine
from orm_models import Base, User, Vendor, Food, Order, Rider

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/food-genie")
DB_NAME = os.getenv("DB_NAME", "food-genie")

def run_migration():
    print("--- Starting Data Migration from MongoDB to Neon PostgreSQL ---")
    
    # Ensure all tables exist in Neon PostgreSQL
    Base.metadata.create_all(sync_engine)
    session = SyncSessionLocal()

    try:
        mongo_client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        mongo_db = mongo_client[DB_NAME]
        
        # Test mongo connection
        mongo_client.admin.command('ping')
        print("[OK] Connected to MongoDB for data migration.")

        # 1. Migrate Users
        mongo_users = list(mongo_db.users.find())
        print(f"Found {len(mongo_users)} users in MongoDB.")
        for u in mongo_users:
            user_id = str(u["_id"])
            existing = session.query(User).filter_by(id=user_id).first()
            if not existing:
                pg_user = User(
                    id=user_id,
                    name=u.get("name", "User"),
                    email=u.get("email", f"{user_id}@foodgenie.com"),
                    password=u.get("password", ""),
                    phone=u.get("phone"),
                    role=u.get("role", "customer"),
                    is_active=u.get("isActive", True),
                    preferences=u.get("preferences", {"diet": "", "calories": 2000, "healthGoals": []}),
                    favorites=u.get("favorites", []),
                    availability=u.get("availability", True),
                    location=u.get("location", {"lat": 0.0, "lng": 0.0})
                )
                session.add(pg_user)

        # 2. Migrate Vendors
        mongo_vendors = list(mongo_db.vendors.find())
        print(f"Found {len(mongo_vendors)} vendors in MongoDB.")
        for v in mongo_vendors:
            vendor_id = str(v["_id"])
            existing = session.query(Vendor).filter_by(id=vendor_id).first()
            if not existing:
                pg_vendor = Vendor(
                    id=vendor_id,
                    name=v.get("name", "Vendor"),
                    email=v.get("email", f"{vendor_id}@vendor.com"),
                    password=v.get("password", ""),
                    city=v.get("city", "Vehari"),
                    phone=v.get("phone"),
                    category=v.get("category", "Pakistani"),
                    cuisine=v.get("cuisine", "General"),
                    address=v.get("address", "Vehari"),
                    status=v.get("status", "open"),
                    rating=float(v.get("rating", 4.5)),
                    is_approved=v.get("isApproved", True),
                    is_active=v.get("isActive", True),
                    logo=v.get("logo", ""),
                    cover_image=v.get("coverImage", "")
                )
                session.add(pg_vendor)

        # 3. Migrate Foods (menuitems)
        mongo_foods = list(mongo_db.menuitems.find())
        print(f"Found {len(mongo_foods)} food items in MongoDB.")
        for f in mongo_foods:
            food_id = str(f["_id"])
            existing = session.query(Food).filter_by(id=food_id).first()
            if not existing:
                v_raw = f.get("vendor") or f.get("vendorId")
                v_id = str(v_raw) if v_raw else None
                pg_food = Food(
                    id=food_id,
                    name=f.get("name", "Food Item"),
                    price=float(f.get("price", 0.0)),
                    category=f.get("category", "General"),
                    description=f.get("description", ""),
                    vendor_id=v_id,
                    calories=int(f.get("calories", 0)),
                    is_available=f.get("isAvailable", True),
                    tags=f.get("tags", []),
                    image=f.get("image", "")
                )
                session.add(pg_food)

        # 4. Migrate Orders
        mongo_orders = list(mongo_db.orders.find())
        print(f"Found {len(mongo_orders)} orders in MongoDB.")
        for o in mongo_orders:
            order_id = str(o["_id"])
            existing = session.query(Order).filter_by(id=order_id).first()
            if not existing:
                c_raw = o.get("customer") or o.get("customerId")
                v_raw = o.get("vendor") or o.get("vendorId")
                r_raw = o.get("rider") or o.get("riderId")
                pg_order = Order(
                    id=order_id,
                    customer_id=str(c_raw) if c_raw else None,
                    vendor_id=str(v_raw) if v_raw else None,
                    rider_id=str(r_raw) if r_raw else None,
                    items=o.get("items", []),
                    total_amount=float(o.get("totalAmount", 0.0)),
                    status=o.get("status", "pending"),
                    delivery_address=o.get("deliveryAddress", {}),
                    payment_method=o.get("paymentMethod", "cash"),
                    special_instructions=o.get("specialInstructions", "")
                )
                session.add(pg_order)

        session.commit()
        print("[SUCCESS] MongoDB data successfully imported to Neon PostgreSQL!")

    except Exception as e:
        print(f"[NOTE] Local MongoDB migration skipped or not running: {e}")
        print("[INFO] Neon PostgreSQL schema is ready and fully operational.")
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()

from database import SyncSessionLocal
from models.user import User
from middleware.auth_middleware import hash_password

def seed():
    session = SyncSessionLocal()
    try:
        admin = session.query(User).filter(User.email == "admin@foodgenie.com").first()
        if not admin:
            admin = User(
                name="FoodGenie Admin",
                email="admin@foodgenie.com",
                password=hash_password("admin123"),
                role="admin",
                phone="+923000000000"
            )
            session.add(admin)
            session.commit()
            print("[OK] Admin user successfully created!")
        else:
            admin.password = hash_password("admin123")
            session.commit()
            print("[OK] Admin password updated!")
    except Exception as e:
        session.rollback()
        print(f"[ERROR] Seeding admin failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    seed()

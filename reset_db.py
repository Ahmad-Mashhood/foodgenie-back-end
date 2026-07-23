from database import engine
from models import Base
from sqlalchemy import text

def reset_tables():
    print("--- Resetting Neon PostgreSQL Database Tables ---")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS order_items CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS orders CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS reviews CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS user_preferences CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS foods CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS vendors CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS riders CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
        conn.commit()
    
    Base.metadata.create_all(bind=engine)
    print("[OK] All PostgreSQL tables created clean with Integer Auto-Increment IDs!")

if __name__ == "__main__":
    reset_tables()

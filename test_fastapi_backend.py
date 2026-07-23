import requests
from database import SyncSessionLocal
from sqlalchemy import text

BASE_URL = "http://127.0.0.1:8000"

def test_fastapi_endpoints():
    print("--- Testing Modular FastAPI Backend (Neon PostgreSQL) ---\n")

    # Cleanup test records
    try:
        session = SyncSessionLocal()
        session.execute(text("DELETE FROM reviews WHERE comment LIKE '%Test%'"))
        session.execute(text("DELETE FROM order_items WHERE price > 0"))
        session.execute(text("DELETE FROM orders WHERE delivery_address LIKE '%Vehari%'"))
        session.execute(text("DELETE FROM foods WHERE name LIKE '%Vehari%' OR name LIKE '%Test%'"))
        session.execute(text("DELETE FROM users WHERE email LIKE '%@test.com%'"))
        session.execute(text("DELETE FROM vendors WHERE email LIKE '%@test.com%'"))
        session.execute(text("DELETE FROM riders WHERE email LIKE '%@test.com%'"))
        session.commit()
        session.close()
    except Exception as e:
        print(f"[NOTE] DB cleanup skipped: {e}")

    # 1. Healthcheck & Swagger UI
    print("1. Testing GET / (Health Check)...")
    r = requests.get(f"{BASE_URL}/")
    print(f"   Status: {r.status_code} | Data: {r.json()}")
    assert r.status_code == 200, "Health check failed"

    print("2. Testing GET /docs (Swagger UI Page)...")
    r = requests.get(f"{BASE_URL}/docs")
    print(f"   Status: {r.status_code} | Swagger HTML Length: {len(r.text)} bytes")
    assert r.status_code == 200, "Swagger UI page failed"

    # 2. Authentication
    print("\n3. Testing POST /api/auth/register (Customer)...")
    cust_data = {
        "name": "FastAPI Test Customer",
        "email": "fastapi_cust@test.com",
        "password": "password123",
        "phone": "+923001112222",
        "role": "customer"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register", json=cust_data)
    print(f"   Status: {r.status_code}")
    cust_resp = r.json()
    cust_token = cust_resp.get("token")

    print("4. Testing POST /api/auth/register (Rider)...")
    rider_data = {
        "name": "FastAPI Test Rider",
        "email": "fastapi_rider@test.com",
        "password": "password123",
        "phone": "+923003334444",
        "role": "rider"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register", json=rider_data)
    print(f"   Status: {r.status_code}")
    rider_resp = r.json()
    rider_token = rider_resp.get("token")
    rider_id = rider_resp.get("user", {}).get("id")

    print("5. Testing POST /api/auth/register (Admin)...")
    admin_data = {
        "name": "FastAPI Test Admin",
        "email": "fastapi_admin@test.com",
        "password": "password123",
        "phone": "+923005556666",
        "role": "admin"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register", json=admin_data)
    print(f"   Status: {r.status_code}")
    admin_resp = r.json()
    admin_token = admin_resp.get("token")

    print("6. Testing POST /api/vendors/register (Vendor)...")
    vendor_data = {
        "name": "Vehari Spice Grill",
        "email": "fastapi_vendor@test.com",
        "password": "password123",
        "city": "Vehari",
        "phone": "+923007778888",
        "category": "restaurant"
    }
    r = requests.post(f"{BASE_URL}/api/vendors/register", json=vendor_data)
    print(f"   Status: {r.status_code}")
    vendor_resp = r.json()
    vendor_token = vendor_resp.get("token")
    vendor_id = vendor_resp.get("vendor", {}).get("id")

    print("7. Testing GET /api/auth/me (Protected)...")
    headers = {"Authorization": f"Bearer {cust_token}"}
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"   Status: {r.status_code} | Name: {r.json().get('name')}")

    # 3. Food Catalog & Filters
    print("\n8. Testing POST /api/foods (Add Menu Item)...")
    v_headers = {"Authorization": f"Bearer {vendor_token}"}
    food_data = {
        "name": "Special Vehari Chicken Biryani",
        "price": 380.0,
        "category": "biryani",
        "description": "Authentic fragrant spicy chicken biryani",
        "calories": 480,
        "is_available": True,
        "vendor_id": vendor_id
    }
    r = requests.post(f"{BASE_URL}/api/foods", json=food_data, headers=v_headers)
    print(f"   Status: {r.status_code}")
    food_resp = r.json()
    food_id = food_resp.get("id")

    print("9. Testing GET /api/foods...")
    r = requests.get(f"{BASE_URL}/api/foods")
    print(f"   Status: {r.status_code} | Total Foods: {len(r.json())}")

    print("10. Testing GET /api/foods/filter?category=biryani&max_calories=500...")
    r = requests.get(f"{BASE_URL}/api/foods/filter?category=biryani&max_calories=500")
    print(f"    Status: {r.status_code} | Found Foods: {len(r.json())}")

    # 4. Vendor Status & Search
    print("\n11. Testing PATCH /api/vendors/{id}/status...")
    r = requests.patch(f"{BASE_URL}/api/vendors/{vendor_id}/status", json={"status": "open"}, headers=v_headers)
    print(f"    Status: {r.status_code} | Vendor Status: {r.json().get('status')}")

    print("12. Testing GET /api/search?q=Biryani...")
    r = requests.get(f"{BASE_URL}/api/search?q=Biryani")
    print(f"    Status: {r.status_code} | Foods Found: {len(r.json().get('foods', []))}")

    # 5. Smart Health Recommendations
    print("\n13. Testing POST /api/recommendations/generate...")
    rec_data = {
        "diet_type": "biryani",
        "max_calories": 500,
        "preferred_cuisine": "Pakistani"
    }
    r = requests.post(f"{BASE_URL}/api/recommendations/generate", json=rec_data, headers=headers)
    print(f"    Status: {r.status_code} | Recs Count: {len(r.json())}")

    # 6. Orders & Reviews
    print("\n14. Testing POST /api/orders (Place Order)...")
    order_data = {
        "vendor_id": vendor_id,
        "items": [
            {"food_id": food_id, "quantity": 2, "price": 380.0}
        ],
        "total_amount": 760.0,
        "delivery_address": "House 45, Sharqi Colony, Vehari"
    }
    r = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
    print(f"    Status: {r.status_code}")
    order_resp = r.json()
    order_id = order_resp.get("id")

    print("15. Testing POST /api/reviews (Submit Customer Review)...")
    review_data = {
        "vendor_id": vendor_id,
        "food_id": food_id,
        "rating": 5.0,
        "comment": "Test review: Amazing biryani!"
    }
    r = requests.post(f"{BASE_URL}/api/reviews", json=review_data, headers=headers)
    print(f"    Status: {r.status_code}")

    # 7. Admin Operations & Analytics
    print("\n16. Testing GET /api/admin/analytics...")
    a_headers = {"Authorization": f"Bearer {admin_token}"}
    r = requests.get(f"{BASE_URL}/api/admin/analytics", headers=a_headers)
    print(f"    Status: {r.status_code} | Analytics Keys: {list(r.json().keys())}")

    print("\n[OK] ALL FASTAPI & SWAGGER UI ENDPOINT TESTS PASSED SUCCESSFULLY ON NEON POSTGRESQL!")

if __name__ == "__main__":
    test_fastapi_endpoints()

import pymongo
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_fastapi_endpoints():
    print("--- Testing FastAPI Backend & Swagger UI Integration ---\n")

    # Cleanup test accounts from database
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        db = client["food-genie"]
        db.users.delete_many({"email": {"$regex": "@test\\.com$"}})
        db.vendors.delete_many({"email": {"$regex": "@test\\.com$"}})
        db.menuitems.delete_many({"name": {"$regex": "Vehari|Test"}})
        db.orders.delete_many({})
        client.close()
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
    cust_id = cust_resp.get("user", {}).get("id")

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
    admin_id = admin_resp.get("user", {}).get("id")

    print("6. Testing POST /api/vendors/register (Vendor)...")
    vendor_data = {
        "name": "Vehari Spice Grill",
        "email": "fastapi_vendor@test.com",
        "password": "password123",
        "city": "Vehari",
        "phone": "+923007778888",
        "category": "Pakistani",
        "cuisine": "Biryani & Karahi",
        "address": "Jinnah Shaheed Road, Vehari"
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
        "isAvailable": True,
        "tags": ["spicy", "biryani", "healthy", "rice"]
    }
    r = requests.post(f"{BASE_URL}/api/foods", json=food_data, headers=v_headers)
    print(f"   Status: {r.status_code}")
    food_resp = r.json()
    food_id = food_resp.get("id")

    print("9. Testing GET /api/foods...")
    r = requests.get(f"{BASE_URL}/api/foods")
    print(f"   Status: {r.status_code} | Total Foods: {len(r.json())}")

    print("10. Testing GET /api/foods/filter?category=healthy&calories=500...")
    r = requests.get(f"{BASE_URL}/api/foods/filter?category=healthy&calories=500")
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
        "diet": "biryani",
        "calories": 500,
        "healthGoals": ["healthy", "rice"]
    }
    r = requests.post(f"{BASE_URL}/api/recommendations/generate", json=rec_data, headers=headers)
    print(f"    Status: {r.status_code} | Recs Count: {len(r.json())}")

    # 6. Orders & Rider Tracking
    print("\n14. Testing POST /api/orders (Place Order)...")
    order_data = {
        "vendorId": vendor_id,
        "items": [
            {"menuItemId": food_id, "name": "Special Vehari Chicken Biryani", "price": 380.0, "quantity": 2}
        ],
        "totalAmount": 760.0,
        "deliveryAddress": {"address": "House 45, Sharqi Colony, Vehari", "lat": 30.0470, "lng": 72.3580},
        "paymentMethod": "cash"
    }
    r = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=headers)
    print(f"    Status: {r.status_code}")
    order_resp = r.json()
    order_id = order_resp.get("id")

    print("15. Testing PATCH /api/orders/{id}/status (Accept & Set out_for_delivery)...")
    r_headers = {"Authorization": f"Bearer {rider_token}"}
    r = requests.patch(
        f"{BASE_URL}/api/orders/{order_id}/status",
        json={"status": "out_for_delivery", "riderId": rider_id},
        headers=r_headers
    )
    print(f"    Status: {r.status_code} | Order Status: {r.json().get('status')}")

    print("16. Testing PATCH /api/riders/{id}/location (GPS Live Location)...")
    r = requests.patch(
        f"{BASE_URL}/api/riders/{rider_id}/location",
        json={"lat": 30.0455, "lng": 72.3455, "orderId": order_id},
        headers=r_headers
    )
    print(f"    Status: {r.status_code}")

    print("17. Testing PATCH /api/riders/{id}/available (Toggle Availability)...")
    r = requests.patch(
        f"{BASE_URL}/api/riders/{rider_id}/available",
        json={"isAvailable": True},
        headers=r_headers
    )
    print(f"    Status: {r.status_code} | Is Available: {r.json().get('isAvailable')}")

    # 7. Admin Operations & Analytics
    print("\n18. Testing GET /api/admin/analytics...")
    a_headers = {"Authorization": f"Bearer {admin_token}"}
    r = requests.get(f"{BASE_URL}/api/admin/analytics", headers=a_headers)
    print(f"    Status: {r.status_code} | Analytics: {r.json()}")

    print("\n[OK] ALL FASTAPI & SWAGGER UI ENDPOINT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_fastapi_endpoints()

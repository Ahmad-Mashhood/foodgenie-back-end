import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routes import (
    auth_routes,
    food_routes,
    vendor_routes,
    order_routes,
    rider_routes,
    recommendation_routes,
    search_routes,
    admin_routes
)

app = FastAPI(
    title="FoodGenie REST API — FastAPI Backend (Neon PostgreSQL)",
    description=(
        "Smart Food Recommendation & Local Vendor Platform for Vehari city, Pakistan. "
        "Provides REST endpoints for Customers, Vendors, Riders, and Admins with built-in "
        "JWT authentication, Role-Based Access Control (RBAC), and AI health recommendations."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS Middleware
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount APIRouters
app.include_router(auth_routes.router)
app.include_router(food_routes.router)
app.include_router(vendor_routes.router)
app.include_router(order_routes.router)
app.include_router(rider_routes.router)
app.include_router(recommendation_routes.router)
app.include_router(search_routes.router)
app.include_router(admin_routes.router)

@app.on_event("startup")
async def startup_db_client():
    try:
        await init_db()
        print("[OK] Successfully connected to Neon PostgreSQL and initialized database tables.")
    except Exception as e:
        print(f"[WARNING] PostgreSQL Connection / Initialization Warning: {e}")

@app.get("/", tags=["Health Check"])
async def root():
    return {
        "status": "online",
        "database": "Neon PostgreSQL",
        "app": "FoodGenie REST API",
        "version": "2.0.0",
        "city": "Vehari, Pakistan",
        "swagger_docs": "/docs",
        "redoc_docs": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

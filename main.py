import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_sync_db
from routes import (
    auth,
    foods,
    vendors,
    orders,
    riders,
    recommendations,
    search,
    admin,
    reviews,
    compatibility_routes
)

app = FastAPI(
    title="FoodGenie REST API — FastAPI Backend",
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
    "http://localhost:5173",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:5174",
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
app.include_router(auth.router)
app.include_router(foods.router)
app.include_router(vendors.router)
app.include_router(orders.router)
app.include_router(riders.router)
app.include_router(recommendations.router)
app.include_router(search.router)
app.include_router(admin.router)
app.include_router(reviews.router)
app.include_router(compatibility_routes.router)

@app.on_event("startup")
def startup_db_client():
    try:
        init_sync_db()
        print("[OK] Successfully connected to Neon PostgreSQL and created all database tables automatically.")
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

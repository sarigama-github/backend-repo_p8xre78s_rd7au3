import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Project, Order

app = FastAPI(title="Custom Creations Co. API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Custom Creations Co. API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Seed utilities
class SeedResponse(BaseModel):
    products: int
    projects: int

@app.post("/api/seed", response_model=SeedResponse)
def seed_data():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Only seed if empty
    products_count = db["product"].count_documents({})
    projects_count = db["project"].count_documents({})

    if products_count == 0:
        demo_products = [
            Product(title="Custom Performance Hoodie", description="Breathable fabric, embroidered logos", price=79.0, category="clothing", image_url="/images/hoodie.jpg", tags=["hoodie","embroidery"]),
            Product(title="Carbon Fiber Wrap Kit", description="Premium vehicle vinyl wrap kit", price=499.0, category="vehicle", image_url="/images/wrap.jpg", tags=["wrap","vehicle"]),
            Product(title="Laser-Engraved Power Bank", description="10,000mAh with custom engraving", price=39.0, category="gadgets", image_url="/images/powerbank.jpg", tags=["engraving","gift"]),
        ]
        for p in demo_products:
            create_document("product", p)

    if projects_count == 0:
        demo_projects = [
            Project(title="Track-Ready Mustang Wrap", summary="Matte black with neon accents", service="vehicle", hero_image="/images/mustang.jpg", gallery=["/images/mustang1.jpg","/images/mustang2.jpg"], client="Northshore Racing"),
            Project(title="Startup Team Jerseys", summary="Custom jerseys with heat-press numbers", service="clothing", hero_image="/images/jerseys.jpg", gallery=["/images/jersey1.jpg"], client="Team Nova"),
            Project(title="Corporate Gift Set", summary="Branded gadgets pack for conference", service="gadgets", hero_image="/images/gifts.jpg", gallery=["/images/gift1.jpg"], client="Acme Corp"),
        ]
        for pr in demo_projects:
            create_document("project", pr)

    return SeedResponse(products=db["product"].count_documents({}), projects=db["project"].count_documents({}))

# Public query endpoints

@app.get("/api/products")
def list_products(category: Optional[str] = None):
    filter_dict = {"category": category} if category else {}
    docs = get_documents("product", filter_dict)
    # Convert ObjectId to string
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

@app.get("/api/projects")
def list_projects(service: Optional[str] = None):
    filter_dict = {"service": service} if service else {}
    docs = get_documents("project", filter_dict)
    for d in docs:
        d["_id"] = str(d.get("_id"))
    return docs

# Orders endpoint (create only for now)

@app.post("/api/orders")
def create_order(order: Order):
    order_id = create_document("order", order)
    return {"id": order_id, "status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

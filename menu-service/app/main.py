from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(
    title="FoodOps Menu Service",
    description="Manages the restaurant menu - items, categories and prices",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory menu data (in production this would be a database)
MENU_ITEMS = {
    "1": {"id": "1", "name": "Grilled Chicken Breast", "category": "mains", "price": 45.0, "available": True},
    "2": {"id": "2", "name": "Beef Burger", "category": "mains", "price": 55.0, "available": True},
    "3": {"id": "3", "name": "Grilled Salmon", "category": "mains", "price": 75.0, "available": True},
    "4": {"id": "4", "name": "Caesar Salad", "category": "starters", "price": 30.0, "available": True},
    "5": {"id": "5", "name": "Tomato Soup", "category": "starters", "price": 25.0, "available": True},
    "6": {"id": "6", "name": "Chocolate Lava Cake", "category": "desserts", "price": 35.0, "available": True},
    "7": {"id": "7", "name": "Cheesecake", "category": "desserts", "price": 30.0, "available": True},
    "8": {"id": "8", "name": "Fresh Orange Juice", "category": "drinks", "price": 20.0, "available": True},
    "9": {"id": "9", "name": "Sparkling Water", "category": "drinks", "price": 10.0, "available": True},
}


class MenuItem(BaseModel):
    id: str
    name: str
    category: str
    price: float
    available: bool


@app.get("/health")
def health_check():
    """Health check endpoint - used by Kubernetes liveness probe"""
    return {"status": "healthy", "service": "menu-service"}


@app.get("/menu", response_model=List[MenuItem])
def get_full_menu():
    """Returns all available menu items"""
    return [item for item in MENU_ITEMS.values() if item["available"]]


@app.get("/menu/{category}", response_model=List[MenuItem])
def get_menu_by_category(category: str):
    """Returns menu items filtered by category (mains, starters, desserts, drinks)"""
    items = [item for item in MENU_ITEMS.values() if item["category"] == category and item["available"]]
    if not items:
        raise HTTPException(status_code=404, detail=f"No items found in category: {category}")
    return items


@app.get("/item/{item_id}", response_model=MenuItem)
def get_item(item_id: str):
    """Returns a single menu item by ID - called by Order Service to validate orders"""
    if item_id not in MENU_ITEMS:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return MENU_ITEMS[item_id]


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

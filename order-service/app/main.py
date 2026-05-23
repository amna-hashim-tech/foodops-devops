from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
import uuid
import os
from datetime import datetime

app = FastAPI(
    title="FoodOps Order Service",
    description="Handles order placement and tracking. Talks to Menu Service to validate items.",
    version="1.0.0"
)

# Menu Service URL - injected via environment variable (set in Kubernetes deployment)
MENU_SERVICE_URL = os.getenv("MENU_SERVICE_URL", "http://menu-service:8000")

# In-memory order store (in production this would be a database)
ORDERS = {}


class OrderItem(BaseModel):
    item_id: str
    quantity: int


class OrderRequest(BaseModel):
    customer_name: str
    items: List[OrderItem]


class Order(BaseModel):
    order_id: str
    customer_name: str
    items: List[dict]
    total_price: float
    status: str
    created_at: str


@app.get("/health")
def health_check():
    """Health check endpoint - used by Kubernetes liveness probe"""
    return {"status": "healthy", "service": "order-service"}


@app.post("/order", response_model=Order)
async def place_order(order_request: OrderRequest):
    """
    Place a new order.
    Calls Menu Service to validate each item exists and get its price.
    This is real microservice communication inside the Kubernetes cluster.
    """
    order_items = []
    total_price = 0.0

    async with httpx.AsyncClient() as client:
        for order_item in order_request.items:
            # Call Menu Service to validate item and get price
            try:
                response = await client.get(f"{MENU_SERVICE_URL}/item/{order_item.item_id}")
            except httpx.ConnectError:
                raise HTTPException(
                    status_code=503,
                    detail="Menu Service unavailable. Please try again."
                )

            if response.status_code == 404:
                raise HTTPException(
                    status_code=400,
                    detail=f"Item {order_item.item_id} does not exist on the menu"
                )

            menu_item = response.json()

            if not menu_item["available"]:
                raise HTTPException(
                    status_code=400,
                    detail=f"{menu_item['name']} is currently unavailable"
                )

            item_total = menu_item["price"] * order_item.quantity
            total_price += item_total

            order_items.append({
                "item_id": order_item.item_id,
                "name": menu_item["name"],
                "quantity": order_item.quantity,
                "unit_price": menu_item["price"],
                "item_total": item_total
            })

    order_id = str(uuid.uuid4())[:8].upper()
    order = {
        "order_id": order_id,
        "customer_name": order_request.customer_name,
        "items": order_items,
        "total_price": round(total_price, 2),
        "status": "confirmed",
        "created_at": datetime.utcnow().isoformat()
    }

    ORDERS[order_id] = order
    return order


@app.get("/order/{order_id}", response_model=Order)
def get_order(order_id: str):
    """Get order status and details by order ID"""
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return ORDERS[order_id]


@app.get("/orders", response_model=List[Order])
def get_all_orders():
    """Returns all orders - useful for the demo"""
    return list(ORDERS.values())


@app.patch("/order/{order_id}/status")
def update_order_status(order_id: str, status: str):
    """Update order status (confirmed → preparing → ready → delivered)"""
    valid_statuses = ["confirmed", "preparing", "ready", "delivered", "cancelled"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    ORDERS[order_id]["status"] = status
    return {"order_id": order_id, "status": status, "message": "Status updated"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

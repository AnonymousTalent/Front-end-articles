from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uuid
import math
from . import sheets_service

# --- Pydantic Models for Core Data Structures ---

class Location(BaseModel):
    lat: float
    lon: float

class Order(BaseModel):
    id: str = str(uuid.uuid4())
    description: str
    pickup: Location
    dropoff: Location
    status: str = "pending" # e.g., pending, assigned, delivered
    assigned_to: Optional[str] = None

class Rider(BaseModel):
    id: str
    name: str
    location: Location
    status: str = "available" # e.g., available, on_delivery

# --- In-Memory Database ---

db_orders: Dict[str, Order] = {}
db_riders: Dict[str, Rider] = {
    "rider-001": Rider(id="rider-001", name="Flash", location=Location(lat=25.034, lon=121.564)),
    "rider-002": Rider(id="rider-002", name="Speedy", location=Location(lat=25.047, lon=121.517)),
}

# --- FastAPI Application ---

app = FastAPI(
    title="AI Dispatch System API",
    description="Core API for managing orders and riders.",
    version="0.1.0"
)

# --- Helper Functions ---

def calculate_distance(loc1: Location, loc2: Location) -> float:
    """
    Calculate the simple Euclidean distance between two locations.
    This is a simplified distance metric.
    """
    return math.sqrt((loc1.lat - loc2.lat)**2 + (loc1.lon - loc2.lon)**2)

@app.get("/")
def read_root():
    return {"message": "AI Dispatch System Backend is running."}

# --- API Endpoints ---

# --- Order Endpoints ---

@app.post("/orders", response_model=Order, status_code=201)
def create_order(order_in: Order):
    """
    Create a new order. The ID is handled by the model's default.
    """
    if order_in.id in db_orders:
        # This handles the rare case of a UUID collision
        raise HTTPException(status_code=409, detail="Order ID already exists")
    db_orders[order_in.id] = order_in
    sheets_service.log_order(order_in)
    return order_in

@app.get("/orders", response_model=List[Order])
def get_orders():
    """
    Retrieve a list of all current orders.
    """
    return list(db_orders.values())

@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    """
    Retrieve a specific order by its ID.
    """
    if order_id not in db_orders:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_orders[order_id]

# --- Rider Endpoints ---

@app.post("/riders/{rider_id}/location", response_model=Rider)
def update_rider_location(rider_id: str, location: Location):
    """
    Update a rider's current location.
    """
    if rider_id not in db_riders:
        raise HTTPException(status_code=404, detail="Rider not found")
    db_riders[rider_id].location = location
    return db_riders[rider_id]

@app.get("/riders", response_model=List[Rider])
def get_riders():
    """
    Retrieve a list of all riders.
    """
    return list(db_riders.values())

@app.get("/riders/{rider_id}", response_model=Rider)
def get_rider(rider_id: str):
    """
    Retrieve a specific rider by their ID.
    """
    if rider_id not in db_riders:
        raise HTTPException(status_code=404, detail="Rider not found")
    return db_riders[rider_id]

# --- Dispatch Endpoint ---

class DispatchRequest(BaseModel):
    order_id: str

@app.post("/dispatch", response_model=Order)
def dispatch_order(dispatch_request: DispatchRequest):
    """
    Dispatches an order to the nearest available rider.
    """
    order_id = dispatch_request.order_id
    if order_id not in db_orders:
        raise HTTPException(status_code=404, detail="Order not found")

    order = db_orders[order_id]
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order is not pending")

    available_riders = [rider for rider in db_riders.values() if rider.status == "available"]
    if not available_riders:
        raise HTTPException(status_code=400, detail="No available riders")

    # Find the closest rider
    closest_rider = None
    min_distance = float('inf')

    for rider in available_riders:
        distance = calculate_distance(order.pickup, rider.location)
        if distance < min_distance:
            min_distance = distance
            closest_rider = rider

    if not closest_rider:
        # This case should not be reached if there are available riders, but as a safeguard
        raise HTTPException(status_code=500, detail="Could not determine closest rider")

    # Assign the order
    order.status = "assigned"
    order.assigned_to = closest_rider.id
    closest_rider.status = "on_delivery"

    sheets_service.log_dispatch(order)
    return order

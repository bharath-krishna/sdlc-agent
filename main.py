from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from datetime import datetime

app = FastAPI(
    title='Doll Shop API',
    description='API for managing dolls and playtime reservations.'
)

# --- Data Models ---

class DollMaterial(str, Enum):
    wooden = 'wooden'
    fluffed = 'fluffed'
    electronic = 'electronic'

class Doll(BaseModel):
    id: int
    name: str
    material: DollMaterial
    weight: float  # in kg
    price: float
    description: Optional[str] = None

class Reservation(BaseModel):
    id: int
    customer_name: str
    doll_id: int
    start_time: datetime
    end_time: datetime

# --- In-Memory Databases ---

dolls_db = [
    {'id': 1, 'name': 'Pinocchio', 'material': 'wooden', 'weight': 1.2, 'price': 25.0, 'description': 'Classic wooden doll'},
    {'id': 2, 'name': 'Teddy', 'material': 'fluffed', 'weight': 0.5, 'price': 15.0, 'description': 'Soft and cuddly'}
]
reservations_db = []

# --- Doll Endpoints ---

@app.get('/dolls', response_model=List[Doll], tags=['Dolls'])
def list_dolls(material: Optional[DollMaterial] = None):
    """List all dolls with optional filtering by material."""
    if material:
        return [d for d in dolls_db if d['material'] == material]
    return dolls_db

@app.post('/dolls', response_model=Doll, status_code=201, tags=['Dolls'])
def create_doll(doll: Doll):
    """Create a new doll entry."""
    if any(d['id'] == doll.id for d in dolls_db):
        raise HTTPException(status_code=400, detail='Doll ID already exists')
    dolls_db.append(doll.dict())
    return doll

@app.get('/dolls/{doll_id}', response_model=Doll, tags=['Dolls'])
def get_doll(doll_id: int):
    """Retrieve details of a specific doll."""
    doll = next((d for d in dolls_db if d['id'] == doll_id), None)
    if not doll: raise HTTPException(status_code=404, detail='Doll not found')
    return doll

@app.put('/dolls/{doll_id}', response_model=Doll, tags=['Dolls'])
def update_doll(doll_id: int, updated_doll: Doll):
    """Update doll information."""
    idx = next((i for i, d in enumerate(dolls_db) if d['id'] == doll_id), None)
    if idx is None: raise HTTPException(status_code=404, detail='Doll not found')
    dolls_db[idx] = updated_doll.dict()
    return updated_doll

@app.delete('/dolls/{doll_id}', tags=['Dolls'])
def delete_doll(doll_id: int):
    """Remove a doll from the shop."""
    global dolls_db
    dolls_db = [d for d in dolls_db if d['id'] != doll_id]
    return {'message': 'Doll deleted successfully'}

@app.get('/dolls/price-check/{doll_id}', tags=['Utilities'])
def check_price(doll_id: int):
    """Quickly check the price and weight of a doll."""
    doll = next((d for d in dolls_db if d['id'] == doll_id), None)
    if not doll: raise HTTPException(status_code=404, detail='Doll not found')
    return {'name': doll['name'], 'price': doll['price'], 'weight': doll['weight']}

# --- Reservation Endpoints ---

@app.post('/reservations', response_model=Reservation, status_code=201, tags=['Reservations'])
def create_reservation(res: Reservation):
    """Book a playtime reservation for a doll."""
    if not any(d['id'] == res.doll_id for d in dolls_db):
        raise HTTPException(status_code=404, detail='Doll not found for reservation')
    reservations_db.append(res.dict())
    return res

@app.get('/reservations', response_model=List[Reservation], tags=['Reservations'])
def list_reservations():
    """View all active reservations."""
    return reservations_db

@app.delete('/reservations/{res_id}', tags=['Reservations'])
def delete_reservation(res_id: int):
    """Cancel a reservation."""
    global reservations_db
    reservations_db = [r for r in reservations_db if r['id'] != res_id]
    return {'message': 'Reservation cancelled'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

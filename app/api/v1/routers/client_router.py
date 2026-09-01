"""
app/api/v1/routers/client_router.py — Client endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.client import ClientCreate, ClientOut
from app.services.client_service import ClientService

router = APIRouter(
    prefix="/clients",
    tags=["Clients"],
    dependencies=[Depends(get_current_user)],
)


@router.post("/", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(
    payload: ClientCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new client."""
    return await ClientService.create_client(db, payload)


@router.get("/", response_model=List[ClientOut])
async def list_clients(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all clients."""
    return await ClientService.get_all_clients(db)


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(
    client_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Fetch a single client by ID."""
    return await ClientService.get_client_by_id(db, client_id)

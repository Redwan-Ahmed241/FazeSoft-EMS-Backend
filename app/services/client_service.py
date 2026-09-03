"""
app/services/client_service.py — Business logic for client operations.
"""
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.client import Client
from app.schemas.client import ClientCreate


class ClientService:
    @staticmethod
    async def create_client(db: AsyncSession, payload: ClientCreate) -> Client:
        existing = await db.execute(
            select(Client).where(Client.email == payload.email)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Client with email '{payload.email}' already exists.",
            )

        client = Client(
            client_name=payload.client_name,
            email=payload.email,
            phone=payload.phone,
            company_name=payload.company_name,
            address=payload.address,
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
        return client

    @staticmethod
    async def get_all_clients(db: AsyncSession) -> List[Client]:
        result = await db.execute(
            select(Client).order_by(Client.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_client_by_id(db: AsyncSession, client_id: UUID) -> Client:
        result = await db.execute(
            select(Client).where(Client.client_id == client_id)
        )
        client = result.scalar_one_or_none()
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Client with id={client_id} not found.",
            )
        return client

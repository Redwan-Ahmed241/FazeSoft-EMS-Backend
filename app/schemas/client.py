"""
app/schemas/client.py — Pydantic schemas for Client.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ClientCreate(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1)

class ClientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    client_id: UUID
    client_name: str
    email: str
    phone: str
    company_name: str
    address: str
    created_at: datetime
    updated_at: datetime

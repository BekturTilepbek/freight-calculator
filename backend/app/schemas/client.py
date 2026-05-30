from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class ClientBase(BaseModel):
    name: str
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    name: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class ClientOut(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
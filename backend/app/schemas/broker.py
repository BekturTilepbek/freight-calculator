from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class BrokerBase(BaseModel):
    company_name: str
    mc_number: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class BrokerCreate(BrokerBase):
    pass


class BrokerUpdate(BaseModel):
    company_name: str | None = None
    mc_number: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class BrokerOut(BrokerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
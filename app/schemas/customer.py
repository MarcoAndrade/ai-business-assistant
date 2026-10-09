
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    phone: str | None
    email: str | None

    model_config = ConfigDict(from_attributes=True)
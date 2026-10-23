from pydantic import BaseModel, Field, EmailStr
from typing import Literal

class ShipmentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    status: str = "pending"

class ShipmentModify(BaseModel):
    content: str | None = None
    destination: str | None = None
    status: Literal["pending", "in_transit", "delivered"] | None = None
    customer_id: int | None = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    user_id: int | None = None

    model_config = {"from_attributes": True}


class ShipmentResponse(BaseModel):
    id: int
    content: str
    destination: str
    status: str
    customer_id: int | None = None
    customer: CustomerResponse | None = None

    model_config = {"from_attributes": True}

class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    user_id: int


class CustomerModify(BaseModel):
    name: str | None = None
    user_id: int | None = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    customer_name: str | None = Field(default=None, min_length=1, max_length=100)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"







from datetime import datetime
from typing import Optional, Union, Any
from pydantic import BaseModel, EmailStr, model_validator

class UserBase(BaseModel):
    email: str
    full_name: Optional[str] = None
    name: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def sync_names(cls, data: Any) -> Any:
        if isinstance(data, dict):
            fn = data.get("full_name") or data.get("name")
            if fn:
                data["full_name"] = fn
                data["name"] = fn
        elif hasattr(data, "full_name"):
            fn = getattr(data, "full_name", None)
            if fn:
                setattr(data, "name", fn)
        return data

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(UserBase):
    id: Union[str, int]
    role: str = "USER"
    is_active: bool = True
    created_at: Optional[datetime] = None

    @model_validator(mode="before")
    @classmethod
    def map_id_and_name(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "_id" in data and "id" not in data:
                data["id"] = str(data["_id"])
            fn = data.get("full_name") or data.get("name")
            if fn:
                data["full_name"] = fn
                data["name"] = fn
        return data

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

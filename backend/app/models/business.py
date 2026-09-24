from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.base import BaseMongoModel


class Business(BaseMongoModel):
    name: str = Field(..., description="Business or brand name")
    owner_id: Optional[str] = Field(default=None, description="Primary owner user ID")
    phone_number: Optional[str] = Field(default=None, description="Primary business phone number")
    website: Optional[str] = Field(default=None)
    industry: Optional[str] = Field(default=None)
    timezone: str = Field(default="Asia/Kolkata")
    settings: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = Field(default=True)


class BusinessResponse(BaseModel):
    id: str
    name: str
    owner_id: Optional[str] = None
    phone_number: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    timezone: str = "Asia/Kolkata"
    is_active: bool = True

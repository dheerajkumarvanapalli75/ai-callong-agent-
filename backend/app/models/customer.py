from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.base import TenantScopedModel


class LeadStatus(str, Enum):
    INTERESTED = "INTERESTED"
    NOT_INTERESTED = "NOT_INTERESTED"
    FOLLOW_UP_REQUIRED = "FOLLOW_UP_REQUIRED"
    UNCERTAIN = "UNCERTAIN"
    REGISTERED = "REGISTERED"
    ALREADY_REGISTERED = "ALREADY_REGISTERED"


class Customer(TenantScopedModel):
    customer_id: str = Field(..., description="Unique customer ID within business")
    name: Optional[str] = None
    phone: str = Field(..., description="Normalized E.164 phone number e.g. +14155552671")
    email: Optional[str] = None
    preferred_language: str = Field(default="en")
    lead_status: LeadStatus = Field(default=LeadStatus.UNCERTAIN)
    lead_evidence: Optional[str] = None
    lead_confidence: float = Field(default=0.0)
    do_not_call: bool = Field(default=False)
    consent_recorded: bool = Field(default=False)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class ConversationMessage(TenantScopedModel):
    call_id: str = Field(..., description="Reference to active call session")
    customer_id: str = Field(..., description="Customer ID")
    role: str = Field(..., description="'user', 'agent', or 'system'")
    text: str = Field(..., description="Spoken or generated utterance")
    language: str = Field(default="en")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=lambda: {
        "intent": None,
        "task": None,
        "retrieved_chunk_ids": [],
        "confidence": 1.0,
        "simulated": False
    })

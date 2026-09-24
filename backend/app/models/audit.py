from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import Field
from app.models.base import TenantScopedModel


class AuditLog(TenantScopedModel):
    user_id: Optional[str] = Field(default=None, description="User who executed action")
    user_email: Optional[str] = Field(default=None)
    action: str = Field(..., description="Action name e.g. AGENT_UPDATED, VERSION_PUBLISHED")
    entity_type: str = Field(..., description="Target collection or module name")
    entity_id: Optional[str] = Field(default=None)
    changes: Dict[str, Any] = Field(default_factory=dict, description="Diff or state summary")
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

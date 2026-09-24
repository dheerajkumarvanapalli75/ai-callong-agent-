from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.models.base import TenantScopedModel


class AgentDeploymentStatus(str, Enum):
    DRAFT = "DRAFT"
    TRAINING = "TRAINING"
    TESTING = "TESTING"
    READY = "READY"
    DEPLOYED = "DEPLOYED"


class VersionStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class AgentConfigSnapshot(BaseModel):
    identity: Dict[str, Any] = Field(default_factory=lambda: {
        "name": "", "role": "", "business_name": "", "personality": [], "speaking_style": []
    })
    goal: str = Field(default="")
    languages: List[Dict[str, Any]] = Field(default_factory=list)
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    rules: List[Dict[str, Any]] = Field(default_factory=list)
    examples: List[Dict[str, Any]] = Field(default_factory=list)
    objections: List[Dict[str, Any]] = Field(default_factory=list)
    intents: List[Dict[str, Any]] = Field(default_factory=list)
    lead_rules: List[Dict[str, Any]] = Field(default_factory=list)
    permissions: List[Dict[str, Any]] = Field(default_factory=list)
    handoff_rules: List[Dict[str, Any]] = Field(default_factory=list)
    workflow: Dict[str, Any] = Field(default_factory=dict)
    llm: Dict[str, Any] = Field(default_factory=lambda: {
        "provider": "openai", "model": "gpt-4o-mini", "temperature": 0.3
    })
    knowledge_version: str = Field(default="")


class Agent(TenantScopedModel):
    name: str = Field(..., description="Agent name")
    description: Optional[str] = None
    deployment_status: AgentDeploymentStatus = Field(default=AgentDeploymentStatus.DRAFT)
    draft_config: AgentConfigSnapshot = Field(default_factory=AgentConfigSnapshot)
    active_version_id: Optional[str] = Field(default=None, description="Currently live published version ID")
    phone_number: Optional[str] = Field(default=None)


class AgentVersion(TenantScopedModel):
    agent_id: str = Field(..., description="Parent agent ID")
    version: str = Field(..., description="Semantic version string e.g. v1.0")
    config_snapshot: AgentConfigSnapshot = Field(..., description="Frozen configuration snapshot")
    knowledge_version: str = Field(default="")
    change_summary: str = Field(default="Initial version")
    created_by: str = Field(..., description="User ID who published this version")
    status: VersionStatus = Field(default=VersionStatus.PUBLISHED)

from enum import Enum
from typing import List, Optional
from pydantic import Field
from app.models.base import TenantScopedModel


class KnowledgeCategory(str, Enum):
    BUSINESS = "Business"
    PRODUCTS = "Products"
    SERVICES = "Services"
    PRICING = "Pricing"
    REGISTRATION = "Registration"
    POLICIES = "Policies"
    FAQS = "FAQs"
    CONTACT = "Contact"
    OPERATING_HOURS = "Operating hours"
    OTHER = "Other"


class DocumentType(str, Enum):
    TEXT = "text"
    PDF = "pdf"
    DOCX = "docx"
    FAQ = "faq"
    URL = "url"
    STRUCTURED = "structured"


class IngestionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class KnowledgeDocument(TenantScopedModel):
    title: str = Field(..., description="Document title")
    doc_type: DocumentType = Field(default=DocumentType.TEXT)
    category: KnowledgeCategory = Field(default=KnowledgeCategory.BUSINESS)
    approved: bool = Field(default=False, description="Only approved documents are retrievable")
    source_url: Optional[str] = None
    ingestion_status: IngestionStatus = Field(default=IngestionStatus.PENDING)
    chunk_count: int = Field(default=0)
    version: int = Field(default=1)


class KnowledgeChunk(TenantScopedModel):
    document_id: str = Field(..., description="Parent document ID")
    text: str = Field(..., description="Sanitized chunk text (300-500 tokens)")
    embedding: List[float] = Field(default_factory=list, description="Vector embedding")
    category: KnowledgeCategory = Field(default=KnowledgeCategory.BUSINESS)
    language: str = Field(default="en")
    embedding_model: str = Field(default="text-embedding-3-small")
    doc_version: int = Field(default=1)
    approved: bool = Field(default=False)

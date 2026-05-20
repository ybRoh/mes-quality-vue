"""
표준문서관리 Pydantic 스키마
- Document, DocumentRevision, DocumentAttachment Create/Update/Response
"""

from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import Literal, Optional, List


# ============================================================
# 표준문서
# ============================================================

class DocumentCreate(BaseModel):
    doc_no: str
    doc_type: Literal["MANUAL", "PROCESS", "REGULATION", "FORM"]
    title: str
    department: Optional[str] = None
    revision: int = 1
    status: Literal["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED", "OBSOLETE"] = "DRAFT"
    prepared_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    effective_date: Optional[date] = None


class DocumentUpdate(BaseModel):
    doc_type: Optional[Literal["MANUAL", "PROCESS", "REGULATION", "FORM"]] = None
    title: Optional[str] = None
    department: Optional[str] = None
    revision: Optional[int] = None
    status: Optional[Literal["DRAFT", "IN_REVIEW", "APPROVED", "SUPERSEDED", "OBSOLETE"]] = None
    prepared_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    effective_date: Optional[date] = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doc_id: int
    doc_no: str
    doc_type: str
    title: str
    department: Optional[str] = None
    revision: int
    status: str
    prepared_by: Optional[str] = None
    reviewed_by: Optional[str] = None
    approved_by: Optional[str] = None
    effective_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    revision_count: Optional[int] = None
    attachment_count: Optional[int] = None


# ============================================================
# 문서 개정이력
# ============================================================

class DocumentRevisionCreate(BaseModel):
    revision_no: int
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None


class DocumentRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    revision_id: int
    doc_id: int
    revision_no: int
    change_summary: Optional[str] = None
    changed_by: Optional[str] = None
    previous_status: Optional[str] = None
    new_status: Optional[str] = None
    created_at: Optional[datetime] = None


# ============================================================
# 문서 첨부파일
# ============================================================

class DocumentAttachmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attachment_id: int
    doc_id: int
    file_name: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: Optional[str] = None
    uploaded_by: Optional[str] = None
    created_at: Optional[datetime] = None

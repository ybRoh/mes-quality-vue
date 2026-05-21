"""
Q&A 질문/답변 Pydantic 스키마
"""

import re
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional
from datetime import datetime

_EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class QnaCreate(BaseModel):
    title: str
    question: str
    category: str = "GENERAL"
    is_public: bool = True
    author_email: Optional[str] = None
    author_name: Optional[str] = None

    @field_validator("author_email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not _EMAIL_RE.match(v):
            raise ValueError("올바른 이메일 형식이 아닙니다")
        return v


class QnaUpdate(BaseModel):
    title: Optional[str] = None
    question: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None


class QnaAnswer(BaseModel):
    answer: str


class QnaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    qna_id: int
    title: str
    question: str
    answer: Optional[str] = None
    category: str
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    author_email: Optional[str] = None
    status: str
    is_public: bool
    view_count: int
    answered_by: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

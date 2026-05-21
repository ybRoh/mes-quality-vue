"""
Q&A 질문/답변 Pydantic 스키마
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class QnaCreate(BaseModel):
    title: str
    question: str
    category: str = "GENERAL"
    is_public: bool = True


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
    author_id: str
    author_name: Optional[str] = None
    status: str
    is_public: bool
    view_count: int
    answered_by: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

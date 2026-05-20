"""
공통 Pydantic 스키마
- API 응답 래퍼, 페이지네이션, 인증 관련
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional, Generic, TypeVar, List

T = TypeVar("T")


class DateRange(BaseModel):
    """날짜 범위"""
    from_date: date
    to_date: date


class PageParams(BaseModel):
    """페이지네이션 파라미터"""
    page: int = 1
    size: int = 20


class PagedResponse(BaseModel, Generic[T]):
    """페이지네이션 응답"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class ApiResponse(BaseModel, Generic[T]):
    """API 공통 응답 래퍼"""
    success: bool = True
    data: Optional[T] = None
    message: str = ""


class TokenResponse(BaseModel):
    """JWT 토큰 응답 (deprecated: httpOnly 쿠키로 전환)"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    user_name: str
    role: str


class LoginResponse(BaseModel):
    """로그인 응답 (토큰은 httpOnly 쿠키로 전달)"""
    user_id: str
    user_name: str
    role: str


class LoginRequest(BaseModel):
    """로그인 요청"""
    user_id: str = Field(min_length=1)
    password: str = Field(min_length=1, max_length=128)

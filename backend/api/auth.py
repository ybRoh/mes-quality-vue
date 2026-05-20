"""
인증 API 라우터
- POST /api/auth/login: 로그인 (bcrypt 검증 + JWT 발급)
- GET /api/auth/me: 현재 사용자 정보
"""

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from core.security import create_access_token
from models.existing import SysUser
from schemas.common import LoginRequest, TokenResponse, ApiResponse

router = APIRouter(prefix="/api/auth", tags=["인증"])


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """로그인: bcrypt 비밀번호 검증 후 JWT 토큰 발급"""
    # 사용자 조회
    user = db.query(SysUser).filter(
        SysUser.user_id == request.user_id,
        SysUser.is_active == 1,
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID 또는 비밀번호가 올바르지 않습니다",
        )

    # bcrypt 비밀번호 검증
    password_hash = user.password_hash
    if not (password_hash.startswith("$2b$") or password_hash.startswith("$2a$")):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="비밀번호 해시 형식 오류",
        )

    if not bcrypt.checkpw(request.password.encode(), password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID 또는 비밀번호가 올바르지 않습니다",
        )

    # JWT 토큰 생성
    access_token = create_access_token(data={"sub": user.user_id})

    return TokenResponse(
        access_token=access_token,
        user_id=user.user_id,
        user_name=user.user_name,
        role=user.role,
    )


@router.get("/me")
def get_me(current_user: SysUser = Depends(get_current_user)):
    """현재 로그인 사용자 정보 조회"""
    return {
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "role": current_user.role,
        "department": current_user.department,
    }

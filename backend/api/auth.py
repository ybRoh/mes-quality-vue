"""
인증 API 라우터
- POST /api/auth/login: 로그인 (bcrypt 검증 + JWT httpOnly 쿠키 발급)
- POST /api/auth/logout: 로그아웃 (쿠키 제거)
- GET /api/auth/me: 현재 사용자 정보
"""

import logging
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from api.deps import get_db, get_current_user
from config import settings

logger = logging.getLogger(__name__)
from core.security import create_access_token
from models.existing import SysUser
from schemas.common import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["인증"])

# 쿠키 공통 설정
_COOKIE_KEY = "access_token"
_COOKIE_PATH = "/api"


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """로그인: bcrypt 비밀번호 검증 후 JWT httpOnly 쿠키 발급"""
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
        logger.error("Invalid password hash format for user_id=%s", request.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID 또는 비밀번호가 올바르지 않습니다",
        )

    if not bcrypt.checkpw(request.password.encode(), password_hash.encode()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID 또는 비밀번호가 올바르지 않습니다",
        )

    # JWT 토큰 생성 → httpOnly 쿠키에 저장
    access_token = create_access_token(data={"sub": user.user_id})
    response.set_cookie(
        key=_COOKIE_KEY,
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path=_COOKIE_PATH,
    )

    return LoginResponse(
        user_id=user.user_id,
        user_name=user.user_name,
        role=user.role,
    )


@router.post("/logout")
def logout(response: Response):
    """로그아웃: httpOnly 쿠키 제거"""
    response.delete_cookie(key=_COOKIE_KEY, path=_COOKIE_PATH)
    return {"message": "로그아웃 되었습니다"}


@router.get("/me")
def get_me(current_user: SysUser = Depends(get_current_user)):
    """현재 로그인 사용자 정보 조회"""
    return {
        "user_id": current_user.user_id,
        "user_name": current_user.user_name,
        "role": current_user.role,
        "department": current_user.department,
    }

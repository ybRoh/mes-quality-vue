"""
FastAPI 의존성 주입
- DB 세션 제공
- JWT 기반 현재 사용자 인증
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from database import SessionLocal
from core.security import decode_access_token
from models.existing import SysUser

# OAuth2 토큰 스키마
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> SysUser:
    """JWT 토큰에서 현재 사용자 추출"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(SysUser).filter(
        SysUser.user_id == user_id,
        SysUser.is_active == 1,
    ).first()

    if user is None:
        raise credentials_exception

    return user


def get_current_active_admin(
    current_user: SysUser = Depends(get_current_user),
) -> SysUser:
    """관리자 권한 확인"""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return current_user

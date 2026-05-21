"""
FastAPI 의존성 주입
- DB 세션 제공
- JWT 기반 현재 사용자 인증 (httpOnly 쿠키 + Authorization 헤더 폴백)
- 역할 기반 접근 제어 (RBAC)
- 공용 트랜잭션 래퍼
"""

from contextlib import contextmanager
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError

from database import SessionLocal
from core.security import decode_access_token
from models.existing import SysUser

# Swagger UI용 OAuth2 스키마 (auto_error=False: 쿠키 인증도 지원)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_db():
    """DB 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> SysUser:
    """JWT 토큰에서 현재 사용자 추출 (쿠키 우선, Authorization 헤더 폴백)"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1) Authorization 헤더 (Swagger UI 등)
    # 2) httpOnly 쿠키 폴백
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise credentials_exception

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


def require_role(*allowed_roles: str):
    """역할 기반 접근 제어 의존성 팩토리

    사용 예:
        @router.delete("/{id}", dependencies=[Depends(require_role("ADMIN", "MANAGER"))])
        def delete_item(id: int): ...
    """
    def _check_role(current_user: SysUser = Depends(get_current_user)) -> SysUser:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"이 작업은 {', '.join(allowed_roles)} 권한이 필요합니다",
            )
        return current_user
    return _check_role


def get_optional_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[SysUser]:
    """JWT 인증이 있으면 사용자 반환, 없으면 None (공개 엔드포인트용)"""
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None
    return db.query(SysUser).filter(
        SysUser.user_id == user_id,
        SysUser.is_active == 1,
    ).first()


@contextmanager
def db_transaction(db: Session):
    """Common transaction wrapper to reduce try/commit/rollback boilerplate."""
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise

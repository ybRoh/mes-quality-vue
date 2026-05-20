"""
QMS API 메인 애플리케이션
- FastAPI 앱 생성
- CORS 미들웨어 설정
- 라이프사이클: QMS 테이블 자동 생성
- 모든 라우터 등록
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import engine
from models.base import QmsBase


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 QMS 테이블 자동 생성"""
    # 신규 qms_* 테이블만 생성 (기존 테이블은 절대 건드리지 않음)
    QmsBase.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="QMS API",
    description="IATF 16949 품질경영시스템 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 미들웨어 (Vue.js 개발 서버 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite 개발 서버
        "http://localhost:3000",   # 대체 개발 서버
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 라우터 등록 ──

# 인증
from api.auth import router as auth_router

# 생산분석
from api.analysis.period import router as period_router
from api.analysis.type_based import router as type_router
from api.analysis.equipment import router as equipment_router
from api.analysis.specification import router as spec_router

# 품질 관리
from api.quality.spc import router as spc_router
from api.quality.fmea import router as fmea_router
from api.quality.control_plan import router as cp_router
from api.quality.msa import router as msa_router
from api.quality.ppap import router as ppap_router
from api.quality.apqp import router as apqp_router
from api.quality.claim import router as claim_router
from api.quality.inspection import router as inspection_router

# 기준정보
from api.master.product import router as product_router
from api.master.machine import router as machine_router
from api.master.customer import router as customer_router
from api.master.worker import router as worker_router

# 인증
app.include_router(auth_router)

# 생산분석
app.include_router(period_router)
app.include_router(type_router)
app.include_router(equipment_router)
app.include_router(spec_router)

# 품질 관리
app.include_router(spc_router)
app.include_router(fmea_router)
app.include_router(cp_router)
app.include_router(msa_router)
app.include_router(ppap_router)
app.include_router(apqp_router)
app.include_router(claim_router)
app.include_router(inspection_router)

# 기준정보
app.include_router(product_router)
app.include_router(machine_router)
app.include_router(customer_router)
app.include_router(worker_router)


@app.get("/")
def root():
    """API 루트 헬스체크"""
    return {
        "service": "QMS API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/api/health")
def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "ok"}

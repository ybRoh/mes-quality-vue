# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IATF 16949 Quality Management System (QMS) for automotive parts manufacturing. Full-stack app sharing an existing PostgreSQL database with a sibling `mes-streamlit` project.

## Commands

```bash
# Backend dev server (port 8000)
cd backend && python3 -m uvicorn main:app --reload --port 8000

# Frontend dev server (port 5173, proxies /api to :8000)
cd frontend && npm run dev

# Backend syntax check (no test framework configured)
cd backend && python3 -c "import py_compile,os;[py_compile.compile(os.path.join(r,f),doraise=True) for r,_,fs in os.walk('.') for f in fs if f.endswith('.py')]"

# Frontend type check
cd frontend && npx vue-tsc --noEmit

# Frontend production build
cd frontend && npm run build

# Alembic migration (qms_* tables only)
cd backend && python3 -m alembic revision --autogenerate -m "description"
cd backend && python3 -m alembic upgrade head
```

## Architecture

### Dual ORM Base Pattern

The central design constraint: two SQLAlchemy declarative bases coexist in `models/base.py`.

- **`ExistingBase`** — Maps 38 existing tables from `mes-streamlit` (read-only, never call `create_all`)
- **`QmsBase`** — 23+ QMS tables with `qms_` prefix (safe for `create_all`, managed by Alembic)

`main.py` lifespan calls `QmsBase.metadata.create_all(bind=engine)` on startup. Alembic `env.py` filters migrations to `qms_*` tables via `include_name`.

### Backend (FastAPI)

```
backend/
├── config.py          # pydantic-settings: DATABASE_URL, SECRET_KEY, pagination constants
├── database.py        # engine + SessionLocal (no get_db here — it's in api/deps.py)
├── models/
│   ├── existing.py    # 38 read-only table mappings (Product, Machine, Customer, Claim, etc.)
│   └── iatf.py        # 23+ QMS tables with relationships + cascade deletes
├── api/
│   ├── deps.py        # get_db(), get_current_user(), get_current_active_admin()
│   ├── analysis/      # 4 routers: period, type_based, equipment, specification
│   ├── quality/       # 12 routers: spc, fmea, control_plan, msa, ppap, apqp, claim, inspection, document, audit, training
│   └── master/        # 4 routers: product, machine, customer, worker (read-only)
├── services/
│   ├── spc_service.py # I-MR/Xbar-R charts, Cp/Cpk/Pp/Ppk with SPC constant tables
│   ├── msa_service.py # ANOVA-based GR&R (EV, AV, PV, TV, ndc)
│   └── analysis_service.py  # SQL query functions for production analysis
└── schemas/           # Pydantic v2 request/response models (PagedResponse[T] generic)
```

**Key conventions:**
- All list endpoints return `PagedResponse[T]` with `items`, `total`, `page`, `size`, `pages`
- CRUD routers use private `_build_*_response()` helpers to avoid response construction duplication
- List endpoints batch-load related entities via `in_()` to avoid N+1 queries
- Every `db.commit()` is wrapped in `try/except` with `db.rollback()` on failure
- `datetime.now(timezone.utc)` everywhere (never bare `datetime.now()`)
- Pagination defaults come from `config.settings` (DEFAULT_PAGE_SIZE=20, MASTER_PAGE_SIZE=50)

### Frontend (Vue 3 + TypeScript)

```
frontend/src/
├── api/
│   ├── client.ts      # Axios instance: JWT Bearer interceptor, 401→logout redirect
│   ├── analysis.ts    # 12 analysis endpoints
│   └── quality.ts     # All quality module API calls (spc, fmea, msa, ppap, apqp, claim, document, audit, training)
├── stores/auth.ts     # Pinia: token + user in localStorage, login/logout actions
├── router/index.ts    # Auth guard with JWT expiry check (decodes exp from token)
├── styles/variables.css  # --qms-* CSS custom properties (SAP Fiori color palette)
├── composables/       # useCharts (ECharts base config), usePagination
├── components/
│   ├── common/        # AppLayout, PageHeader, DateRangePicker, KpiCard, DataTable
│   ├── charts/        # LineChart, BarChart, PieChart, SpcChart, ParetoChart, GrrChart
│   └── quality/       # FmeaMatrix, ControlPlanForm, EightDStepper, PpapChecklist
└── views/
    ├── analysis/      # 4 views, each with 3 tab panes
    └── quality/       # 16 views: SPC, FMEA, ControlPlan, MSA, PPAP, APQP, Claim, Inspection,
                       #   Document, Audit (Requirement/Plan/Finding/CorrectiveAction),
                       #   Training, Qualification, Competency
```

**Key conventions:**
- Composition API with `<script setup lang="ts">` exclusively
- Element Plus with Korean locale (`ko`)
- Colors in `<style>` sections use `var(--qms-*)` CSS variables; runtime props use hex literals
- Chart components show "데이터 없음" graphic overlay when data is empty
- API error handling: `catch (e) { console.warn(...); ElMessage.error(...); data.value = [] }`
- Dashboard catch blocks keep demo fallback data (graceful degradation); all other views show empty state
- `vite.config.ts` proxies `/api` → `http://localhost:8000` in dev mode

### Authentication Flow

1. `POST /api/auth/login` validates against existing `sys_user` table (bcrypt), returns JWT
2. Frontend stores token in `localStorage`, adds `Authorization: Bearer` header via Axios interceptor
3. Router `beforeEach` guard decodes JWT payload and checks `exp` field for expiry
4. Backend `get_current_user()` dependency decodes token and verifies user is active

### SPC Calculation Rules

- **I-MR chart** (subgroup_size=1): UCL/LCL = X̄ ± E2·MR̄ where E2=2.66
- **Xbar-R chart** (subgroup_size>1): UCL/LCL = X̄̄ ± A2·R̄
- **Cp/Cpk** (short-term): σ_within = MR̄/d2 (moving range method)
- **Pp/Ppk** (long-term): σ_overall = sample standard deviation (ddof=1)
- SPC constant tables (d2, A2, D3, D4) defined in `services/spc_service.py` for n=2–10

### Database Shared Access

Both this app and `mes-streamlit` connect to the same PostgreSQL instance (`mes_db`). Connection pool: `pool_size=5, max_overflow=10`. The `audit_log` table is shared for unified audit trail. The `claim` and `inspection` tables are read/write from both apps.

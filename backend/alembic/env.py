"""
Alembic 마이그레이션 환경 설정
- qms_* 접두사 테이블만 관리 (기존 테이블 보호)
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

from config import settings
from models.base import QmsBase
import models.iatf  # noqa: F401 - 모델 임포트하여 metadata에 등록

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = QmsBase.metadata


def include_name(name, type_, parent_names):
    """qms_ 접두사 테이블만 마이그레이션 대상으로 포함"""
    if type_ == "table":
        return name.startswith("qms_")
    return True


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_name=include_name,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

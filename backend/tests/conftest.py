import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.security import hash_password
from app.models.user import User, UserRole
from app import models as _models

# In-memory SQLite — быстро и изолированно
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    """Поднимает чистый движок SQLite для каждого теста."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncSession:
    """Сессия с автоматическим откатом."""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session) -> AsyncClient:
    """
    HTTP-клиент, который ходит в наше приложение.
    Подменяем зависимость get_db, чтобы все эндпоинты использовали тестовую БД.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_user(db_session) -> User:
    u = User(
        email="admin@test.com",
        password_hash=hash_password("admin_pass"),
        full_name="Test Admin",
        role=UserRole.ADMIN,
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


@pytest_asyncio.fixture
async def dispatcher_user(db_session) -> User:
    u = User(
        email="dispatcher@test.com",
        password_hash=hash_password("disp_pass"),
        full_name="Test Dispatcher",
        role=UserRole.DISPATCHER,
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


@pytest_asyncio.fixture
async def driver_user(db_session) -> User:
    u = User(
        email="driver@test.com",
        password_hash=hash_password("drv_pass"),
        full_name="Test Driver",
        role=UserRole.DRIVER,
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u


async def _get_token(client: AsyncClient, email: str, password: str) -> str:
    r = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return r.json()["access_token"]


@pytest_asyncio.fixture
async def admin_headers(client, admin_user):
    token = await _get_token(client, "admin@test.com", "admin_pass")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def dispatcher_headers(client, dispatcher_user):
    token = await _get_token(client, "dispatcher@test.com", "disp_pass")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def driver_headers(client, driver_user):
    token = await _get_token(client, "driver@test.com", "drv_pass")
    return {"Authorization": f"Bearer {token}"}
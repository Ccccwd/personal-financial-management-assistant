"""
测试配置文件
包含测试所需的 fixtures 和工具函数
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base, get_db
from app.models.user import User
from main import app


# SQLite 内存数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    数据库会话 fixture

    每个测试函数执行前创建新表，执行后清理。
    """
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    测试客户端 fixture

    使用测试数据库会话覆盖 FastAPI 的 get_db 依赖。
    """
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(client):
    """
    创建测试用户并返回用户信息

    自动注册一个测试用户并返回用户数据。
    """
    # 先尝试注册，如果已存在则忽略
    client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "test123456"
    })
    # 登录获取用户信息
    login_resp = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "test123456"
    })
    assert login_resp.status_code == 200
    return login_resp.json()["data"]


@pytest.fixture
def auth_headers(client, test_user):
    """
    获取认证 headers

    使用测试用户登录并返回包含 JWT Token 的请求头。
    """
    response = client.post("/api/auth/login", json={
        "username": "testuser",
        "password": "test123456"
    })
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_account(client, auth_headers):
    """
    创建测试账户

    为测试用户创建一个默认账户。
    """
    response = client.post("/api/accounts", headers=auth_headers, json={
        "name": "测试账户",
        "type": "cash",
        "initial_balance": "1000.00",
        "is_default": True
    })
    assert response.status_code == 200
    return response.json()["data"]


@pytest.fixture
def test_category(client, auth_headers):
    """
    创建测试分类

    为测试用户创建一个支出分类。
    """
    response = client.post("/api/categories", headers=auth_headers, json={
        "name": "测试分类",
        "type": "expense",
        "icon": "🍔",
        "color": "#FF6B6B"
    })
    assert response.status_code == 200, f"创建分类失败: {response.json()}"
    return response.json()["data"]


@pytest.fixture
def test_income_category(client, auth_headers):
    """
    创建测试收入分类
    """
    response = client.post("/api/categories", headers=auth_headers, json={
        "name": "工资",
        "type": "income",
        "icon": "💰",
        "color": "#4ECDC4"
    })
    assert response.status_code == 200, f"创建收入分类失败: {response.json()}"
    return response.json()["data"]

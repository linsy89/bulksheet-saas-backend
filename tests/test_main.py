"""
测试FastAPI基本功能
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """测试根端点"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "Bulksheet SaaS"
    assert data["version"] == "2.0.0"
    assert data["status"] == "running"


def test_health_check():
    """测试健康检查端点"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "message" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

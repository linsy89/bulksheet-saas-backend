"""
测试Stage 1 API - 属性词生成
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_stage1_generate_success():
    """测试成功生成属性词"""
    response = client.post(
        "/api/stage1/generate",
        json={"concept": "ocean"}
    )

    assert response.status_code == 200
    data = response.json()

    # 验证响应结构
    assert "concept" in data
    assert "candidates" in data
    assert "task_id" in data

    # 验证数据内容
    assert data["concept"] == "ocean"
    assert len(data["candidates"]) > 0

    # 验证候选词结构
    first_candidate = data["candidates"][0]
    assert "word" in first_candidate
    assert "variants" in first_candidate
    assert isinstance(first_candidate["variants"], list)


def test_stage1_generate_chinese():
    """测试中文输入"""
    response = client.post(
        "/api/stage1/generate",
        json={"concept": "海洋"}
    )

    assert response.status_code == 200
    data = response.json()

    assert data["concept"] == "海洋"
    assert len(data["candidates"]) > 0


def test_stage1_generate_empty_concept():
    """测试空概念输入"""
    response = client.post(
        "/api/stage1/generate",
        json={"concept": ""}
    )

    # Pydantic验证应该失败
    assert response.status_code == 422


def test_stage1_generate_long_concept():
    """测试过长概念"""
    long_concept = "a" * 150

    response = client.post(
        "/api/stage1/generate",
        json={"concept": long_concept}
    )

    # Pydantic验证应该失败
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
数据模型定义
使用Pydantic进行数据验证
"""

from pydantic import BaseModel, Field
from typing import List, Optional


# ============ Stage 1: 属性词生成 ============

class AttributeRequest(BaseModel):
    """属性概念输入请求"""
    concept: str = Field(..., min_length=1, max_length=100, description="属性概念，如'ocean', '海洋'")


class AttributeCandidate(BaseModel):
    """属性词候选"""
    word: str
    variants: List[str] = []


class AttributeResponse(BaseModel):
    """属性词候选响应"""
    concept: str
    candidates: List[AttributeCandidate]
    task_id: str

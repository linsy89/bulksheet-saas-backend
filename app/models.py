"""
数据模型定义
使用Pydantic进行数据验证
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ============ Stage 1: 属性词生成 ============

class AttributeRequest(BaseModel):
    """属性概念输入请求"""
    concept: str = Field(..., min_length=1, max_length=100, description="属性概念，如'ocean', '海洋'")
    entity_word: str = Field(default="phone case", description="本体词，如'phone case', 'iphone 16 pro case'")


class AttributeWord(BaseModel):
    """属性词实体 - 核心数据单元"""
    word: str = Field(..., description="属性词（英文）")
    concept: str = Field(..., description="原始属性词概念（中文/英文）")
    type: Literal["original", "synonym", "related", "variant"] = Field(..., description="词汇类型")
    translation: str = Field(..., description="中文翻译和说明")
    use_case: str = Field(..., description="适用场景描述")
    search_value: Literal["high", "medium", "low"] = Field(..., description="搜索价值")
    search_value_stars: int = Field(..., ge=1, le=5, description="搜索价值星级: 1-5")
    recommended: bool = Field(..., description="是否推荐")


class AttributeMetadata(BaseModel):
    """属性词生成元数据"""
    total_count: int = Field(..., description="属性词总数")
    generated_at: str = Field(..., description="生成时间（ISO 8601）")
    original_count: int = Field(default=0, description="原词数量")
    synonym_count: int = Field(default=0, description="同义词数量")
    related_count: int = Field(default=0, description="相近词数量")
    variant_count: int = Field(default=0, description="变体数量")


class AttributeResponse(BaseModel):
    """Stage 1 属性词生成响应"""
    concept: str = Field(..., description="输入的属性概念")
    entity_word: str = Field(..., description="本体词")
    attributes: List[AttributeWord] = Field(..., description="属性词列表")
    task_id: str = Field(..., description="任务ID")
    metadata: AttributeMetadata = Field(..., description="元数据")

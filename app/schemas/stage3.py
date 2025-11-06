"""
Stage 3 Pydantic Schemas
本体词生成、筛选、搜索词组合相关的数据模型
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


# ========== 本体词相关 Schemas ==========

class EntityWordGenerateOptions(BaseModel):
    """生成本体词的选项"""
    max_count: int = Field(default=15, ge=5, le=20, description="最大生成数量")


class EntityWordGenerateRequest(BaseModel):
    """生成本体词的请求"""
    options: Optional[EntityWordGenerateOptions] = None


class EntityWordItem(BaseModel):
    """单个本体词"""
    id: int
    entity_word: str
    type: str
    translation: Optional[str] = None
    use_case: Optional[str] = None
    search_value: str
    search_value_stars: int
    recommended: bool
    source: str
    is_selected: bool

    class Config:
        from_attributes = True


class EntityWordMetadata(BaseModel):
    """本体词元数据统计"""
    total_count: int
    selected_count: int
    type_distribution: dict  # {"original": 1, "synonym": 3, "variant": 8}


class EntityWordGenerateResponse(BaseModel):
    """生成本体词的响应"""
    task_id: str
    entity_words: List[EntityWordItem]
    metadata: EntityWordMetadata
    status: str
    updated_at: datetime


class EntityWordListResponse(BaseModel):
    """查询本体词列表的响应"""
    task_id: str
    entity_words: List[EntityWordItem]
    metadata: EntityWordMetadata


# ========== 本体词选择相关 Schemas ==========

class NewEntityWord(BaseModel):
    """用户新增的自定义本体词"""
    entity_word: str = Field(..., min_length=1, max_length=200)

    @field_validator('entity_word')
    @classmethod
    def validate_entity_word(cls, v: str) -> str:
        """验证本体词格式"""
        import re
        v = v.strip()
        if len(v) == 0:
            raise ValueError("本体词不能为空")
        if len(v) > 200:
            raise ValueError("本体词长度不能超过 200 个字符")
        # 只允许英文、数字、空格、连字符
        if not re.match(r'^[a-zA-Z0-9\s\-]+$', v):
            raise ValueError("本体词只能包含英文字母、数字、空格和连字符")
        if "  " in v:
            raise ValueError("本体词不能包含连续空格")
        return v


class EntityWordSelectionRequest(BaseModel):
    """更新本体词选择的请求"""
    selected_entity_word_ids: List[int] = Field(default_factory=list)
    new_entity_words: List[NewEntityWord] = Field(default_factory=list)
    deleted_entity_word_ids: List[int] = Field(default_factory=list)


class EntityWordSelectionResponse(BaseModel):
    """更新本体词选择的响应"""
    task_id: str
    status: str
    updated_at: datetime
    metadata: dict  # {"selected_count": 6, "total_count": 12, "changes": {...}}


# ========== 搜索词相关 Schemas ==========

class SearchTermGenerateOptions(BaseModel):
    """生成搜索词的选项"""
    max_length: int = Field(default=80, ge=50, le=200, description="最大字符长度")
    deduplicate: bool = Field(default=True, description="是否去重")


class SearchTermGenerateRequest(BaseModel):
    """生成搜索词的请求"""
    options: Optional[SearchTermGenerateOptions] = None


class SearchTermItem(BaseModel):
    """单个搜索词"""
    id: int
    term: str
    attribute_word: str
    entity_word: str
    length: int
    is_valid: bool

    class Config:
        from_attributes = True


class SearchTermMetadata(BaseModel):
    """搜索词元数据统计"""
    total_terms: int
    valid_terms: int
    invalid_terms: int
    attribute_count: int
    entity_word_count: int


class SearchTermGenerateResponse(BaseModel):
    """生成搜索词的响应"""
    task_id: str
    search_terms: List[SearchTermItem]
    metadata: SearchTermMetadata
    status: str
    updated_at: datetime


class SearchTermListResponse(BaseModel):
    """查询搜索词列表的响应"""
    task_id: str
    search_terms: List[SearchTermItem]
    total: int
    page: int
    page_size: int
    filter_by_attribute: Optional[str] = None
    filter_by_entity: Optional[str] = None


class SearchTermBatchDeleteRequest(BaseModel):
    """批量删除搜索词的请求"""
    search_term_ids: List[int] = Field(..., min_length=1)


class SearchTermBatchDeleteResponse(BaseModel):
    """批量删除搜索词的响应"""
    task_id: str
    deleted_count: int
    remaining_count: int
    message: str

"""
Stage 2 Pydantic 数据模型
用于属性词筛选编辑功能
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class AttributeWithSelection(BaseModel):
    """
    带选中状态的属性词模型（用于GET响应）
    """
    id: int = Field(..., description="属性词ID")
    word: str = Field(..., description="属性词")
    concept: str = Field(..., description="原始属性词概念")
    type: Literal["original", "synonym", "related", "variant", "custom"] = Field(
        ..., description="词汇类型"
    )
    translation: str = Field(..., description="中文翻译和说明")
    use_case: str = Field(..., description="适用场景")
    search_value: Literal["high", "medium", "low"] = Field(..., description="搜索价值")
    search_value_stars: int = Field(..., ge=1, le=5, description="搜索价值星级")
    recommended: bool = Field(..., description="是否推荐")
    source: Literal["ai", "user"] = Field(..., description="来源：ai（AI生成）或user（用户添加）")
    is_selected: bool = Field(..., description="是否被选中")

    class Config:
        from_attributes = True  # Pydantic v2语法，替代orm_mode=True


class TaskMetadata(BaseModel):
    """任务元数据"""
    total_count: int = Field(..., description="属性词总数")
    selected_count: int = Field(..., description="已选中数量")
    ai_generated_count: int = Field(..., description="AI生成的数量")
    user_added_count: int = Field(..., description="用户添加的数量")


class TaskDetailResponse(BaseModel):
    """GET /api/stage2/tasks/{task_id} 响应模型"""
    task_id: str = Field(..., description="任务ID")
    concept: str = Field(..., description="属性概念")
    entity_word: str = Field(..., description="本体词")
    status: str = Field(..., description="任务状态")
    attributes: List[AttributeWithSelection] = Field(..., description="属性词列表")
    metadata: TaskMetadata = Field(..., description="元数据统计")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class NewAttributeCreate(BaseModel):
    """新增自定义属性词请求模型"""
    word: str = Field(..., min_length=1, max_length=100, description="属性词")


class UpdateSelectionRequest(BaseModel):
    """PUT /api/stage2/tasks/{task_id}/selection 请求模型"""
    selected_attribute_ids: List[int] = Field(
        default=[], description="选中的属性词ID列表"
    )
    new_attributes: List[NewAttributeCreate] = Field(
        default=[], description="新增的自定义属性词列表"
    )
    deleted_attribute_ids: List[int] = Field(
        default=[], description="要删除的属性词ID列表"
    )


class SelectionChanges(BaseModel):
    """选择变更统计"""
    selected: int = Field(..., description="选中的数量")
    added: int = Field(..., description="新增的数量")
    deleted: int = Field(..., description="删除的数量")


class UpdateSelectionMetadata(BaseModel):
    """更新选择的元数据"""
    selected_count: int = Field(..., description="当前选中总数")
    total_count: int = Field(..., description="属性词总数（不含已删除）")
    changes: SelectionChanges = Field(..., description="本次变更统计")


class UpdateSelectionResponse(BaseModel):
    """PUT /api/stage2/tasks/{task_id}/selection 响应模型"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    updated_at: datetime = Field(..., description="更新时间")
    metadata: UpdateSelectionMetadata = Field(..., description="元数据统计")

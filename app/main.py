"""
Bulksheet SaaS - Minimal FastAPI Application
采用TDD方式，从最简单的功能开始
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
import uuid

from app.models import (
    AttributeRequest,
    AttributeResponse,
    AttributeWord,
    AttributeMetadata
)
from app.schemas.stage2 import (
    TaskDetailResponse,
    UpdateSelectionRequest,
    UpdateSelectionResponse,
    AttributeWithSelection,
    TaskMetadata,
    UpdateSelectionMetadata,
    SelectionChanges
)
from app.config import load_prompt, load_ai_config
from app.services.deepseek_provider import DeepSeekProvider
from app.database import get_db, init_db
from app.crud import task as crud_task
from app.crud import attribute as crud_attribute

app = FastAPI(
    title="Bulksheet SaaS",
    version="2.0.0",
    description="AI-powered Amazon Advertising Bulksheet Generator"
)

# ============ AI 服务初始化 ============

# 加载配置
ai_config = load_ai_config()
active_provider = ai_config["active_provider"]
prompt_version = ai_config["prompt_version"]

# 加载提示词模板
prompt_template = load_prompt("attribute_expert", version=prompt_version)

# 初始化 AI 服务提供商
provider_config = ai_config["providers"][active_provider]
ai_service = DeepSeekProvider(config=provider_config, prompt_template=prompt_template)

print(f"✅ AI 服务已初始化: {active_provider}, 提示词版本: {prompt_version}")

# ============ 数据库初始化 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()

# ============ CORS 配置 ============

# CORS配置 - 允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ 健康检查 ============

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "app": "Bulksheet SaaS",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "message": "API is running"
    }


# ============ 辅助函数 ============

def convert_deepseek_to_standard(deepseek_attr: Dict) -> Dict:
    """
    将 DeepSeek 返回的中文字段转换为标准英文字段

    Args:
        deepseek_attr: DeepSeek API 返回的单个属性词对象（中文字段）

    Returns:
        标准化的属性词对象（英文字段）
    """
    # 词汇类型映射
    type_mapping = {
        "原词": "original",
        "同义词": "synonym",
        "相近词": "related",
        "变体": "variant"
    }

    # 搜索价值映射
    search_value_text = deepseek_attr.get("搜索价值", "")
    if "高" in search_value_text or "⭐⭐⭐⭐⭐" in search_value_text:
        search_value = "high"
        stars = 5
    elif "中高" in search_value_text or "⭐⭐⭐⭐" in search_value_text:
        search_value = "high"
        stars = 4
    elif "中" in search_value_text or "⭐⭐⭐" in search_value_text:
        search_value = "medium"
        stars = 3
    elif "⭐⭐" in search_value_text:
        search_value = "low"
        stars = 2
    else:
        search_value = "low"
        stars = 1

    # 推荐度映射
    recommended = deepseek_attr.get("推荐度", "") == "✅"

    return {
        "word": deepseek_attr.get("属性词", "").strip(),
        "concept": deepseek_attr.get("原始属性词概念", "").strip(),
        "type": type_mapping.get(deepseek_attr.get("词汇类型", ""), "original"),
        "translation": deepseek_attr.get("中文翻译说明", "").strip(),
        "use_case": deepseek_attr.get("适用场景", "").strip(),
        "search_value": search_value,
        "search_value_stars": stars,
        "recommended": recommended
    }


def generate_metadata(attributes: List[AttributeWord]) -> AttributeMetadata:
    """
    生成属性词列表的元数据统计

    Args:
        attributes: 属性词列表

    Returns:
        元数据对象
    """
    type_counts = {
        "original": 0,
        "synonym": 0,
        "related": 0,
        "variant": 0
    }

    for attr in attributes:
        type_counts[attr.type] = type_counts.get(attr.type, 0) + 1

    return AttributeMetadata(
        total_count=len(attributes),
        generated_at=datetime.utcnow().isoformat() + "Z",
        original_count=type_counts["original"],
        synonym_count=type_counts["synonym"],
        related_count=type_counts["related"],
        variant_count=type_counts["variant"]
    )


# ============ Stage 1: 属性词生成 ============

@app.post("/api/stage1/generate", response_model=AttributeResponse)
async def generate_attribute_candidates(
    request: AttributeRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 1: 生成属性词候选

    接收用户输入的属性概念，调用AI生成属性词候选列表

    输入：
    - concept: 属性概念（如"女性"、"ocean"）
    - entity_word: 本体词（如"phone case"，默认值）

    输出：
    - 标准化的属性词列表（英文字段）
    - 每个属性词包含：词本身、类型、翻译、场景、搜索价值、推荐度
    - 元数据统计信息
    """
    try:
        # 调用 AI 服务生成属性词（返回中文字段）
        attributes_data = await ai_service.generate_attributes(request.concept, request.entity_word)

        # 转换为标准格式（中文字段 → 英文字段）
        attributes = [
            AttributeWord(**convert_deepseek_to_standard(attr))
            for attr in attributes_data
        ]

        # 生成元数据
        metadata = generate_metadata(attributes)

        # 生成任务ID（用于后续阶段跟踪）
        task_id = str(uuid.uuid4())

        # ============ 新增：保存到数据库 ============
        try:
            # 创建任务记录
            crud_task.create_task(
                db=db,
                task_id=task_id,
                concept=request.concept,
                entity_word=request.entity_word
            )

            # 准备属性词数据（转换为dict格式）
            attributes_dict = [attr.model_dump() for attr in attributes]

            # 批量创建属性词记录
            crud_attribute.create_attributes_batch(
                db=db,
                task_id=task_id,
                attributes=attributes_dict
            )

            print(f"✅ 任务已保存到数据库: task_id={task_id}, 属性词数量={len(attributes)}")

        except Exception as db_error:
            # 数据库保存失败不影响API响应，只记录错误日志
            print(f"⚠️  数据库保存失败: {str(db_error)}")
            print("注意：API正常返回，但数据未持久化")
        # ============================================

        return AttributeResponse(
            concept=request.concept,
            entity_word=request.entity_word,
            attributes=attributes,
            task_id=task_id,
            metadata=metadata
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成属性词失败: {str(e)}")


# ============ Stage 2: 属性词筛选编辑 ============

@app.get("/api/stage2/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task_detail(task_id: str, db: Session = Depends(get_db)):
    """
    Stage 2: 查询任务详情

    获取任务的完整信息，包括所有属性词和选中状态
    用于任务恢复功能

    Args:
        task_id: 任务ID

    Returns:
        任务详情，包含所有属性词（不含已删除）及其选中状态
    """
    # 查询任务
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 查询属性词（排除已删除）
    attributes_db = crud_attribute.get_attributes_by_task(db, task_id, include_deleted=False)

    # 转换为响应模型
    attributes = [
        AttributeWithSelection.model_validate(attr)
        for attr in attributes_db
    ]

    # 统计元数据
    ai_count = sum(1 for attr in attributes if attr.source == "ai")
    user_count = sum(1 for attr in attributes if attr.source == "user")
    selected_count = sum(1 for attr in attributes if attr.is_selected)

    metadata = TaskMetadata(
        total_count=len(attributes),
        selected_count=selected_count,
        ai_generated_count=ai_count,
        user_added_count=user_count
    )

    return TaskDetailResponse(
        task_id=task.task_id,
        concept=task.concept,
        entity_word=task.entity_word,
        status=task.status,
        attributes=attributes,
        metadata=metadata,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@app.put("/api/stage2/tasks/{task_id}/selection", response_model=UpdateSelectionResponse)
async def update_task_selection(
    task_id: str,
    request: UpdateSelectionRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 2: 更新任务的属性词选择

    保存用户的选择，包括：
    - 勾选/取消勾选属性词
    - 添加自定义属性词
    - 删除属性词（软删除）

    Args:
        task_id: 任务ID
        request: 更新请求，包含选中ID、新增词、删除ID

    Returns:
        更新结果和统计信息
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 1. 更新选中状态
    if request.selected_attribute_ids:
        crud_attribute.update_attributes_selection(
            db, task_id, request.selected_attribute_ids
        )

    # 2. 添加自定义属性词
    added_count = 0
    for new_attr in request.new_attributes:
        crud_attribute.add_custom_attribute(
            db, task_id, new_attr.word, task.concept
        )
        added_count += 1

    # 3. 软删除属性词
    deleted_count = 0
    if request.deleted_attribute_ids:
        deleted_count = crud_attribute.soft_delete_attributes(
            db, task_id, request.deleted_attribute_ids
        )

    # 4. 更新任务状态为"已选择"
    crud_task.update_task_status(db, task_id, "selected")

    # 5. 获取最新统计
    selected_count = crud_attribute.get_selected_count(db, task_id)
    total_count = len(crud_attribute.get_attributes_by_task(db, task_id, include_deleted=False))

    # 6. 获取更新后的任务信息
    task = crud_task.get_task(db, task_id)

    return UpdateSelectionResponse(
        task_id=task.task_id,
        status=task.status,
        updated_at=task.updated_at,
        metadata=UpdateSelectionMetadata(
            selected_count=selected_count,
            total_count=total_count,
            changes=SelectionChanges(
                selected=len(request.selected_attribute_ids),
                added=added_count,
                deleted=deleted_count
            )
        )
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

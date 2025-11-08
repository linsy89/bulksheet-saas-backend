"""
Bulksheet SaaS - Minimal FastAPI Application
采用TDD方式，从最简单的功能开始
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Dict, List
from datetime import datetime
import uuid

from app.models import (
    AttributeRequest,
    AttributeResponse,
    AttributeWord,
    AttributeMetadata,
    # Stage 4
    ProductInfoRequest,
    ProductInfoResponse,
    ProductInfo,
    ExportRequest
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
from app.schemas.stage3 import (
    EntityWordGenerateRequest,
    EntityWordGenerateResponse,
    EntityWordListResponse,
    EntityWordSelectionRequest,
    EntityWordSelectionResponse,
    SearchTermGenerateRequest,
    SearchTermGenerateResponse,
    SearchTermListResponse,
    SearchTermBatchDeleteRequest,
    SearchTermBatchDeleteResponse,
    EntityWordItem,
    EntityWordMetadata,
    SearchTermItem,
    SearchTermMetadata
)
from app.config import load_prompt, load_ai_config
from app.services.deepseek_provider import DeepSeekProvider
from app.services.entity_word_provider import EntityWordProvider
from app.database import get_db, init_db
from app.crud import task as crud_task
from app.crud import attribute as crud_attribute
from app.crud import entity_word as crud_entity_word
from app.crud import search_term as crud_search_term

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

# 初始化 AI 服务提供商（Stage 1 & 2）
provider_config = ai_config["providers"][active_provider]
ai_service = DeepSeekProvider(config=provider_config, prompt_template=prompt_template)

print(f"✅ Stage 1 & 2 AI 服务已初始化: {active_provider}, 提示词版本: {prompt_version}")

# 初始化 Stage 3 AI 服务（本体词生成）
import os
entity_word_prompt_template = load_prompt("entity_word_expert", version="v1")

# 从环境变量读取 API key
api_key_env = provider_config.get("api_key_env", "DEEPSEEK_API_KEY")
deepseek_api_key = os.getenv(api_key_env)

if not deepseek_api_key:
    print(f"⚠️  警告：环境变量 {api_key_env} 未设置，Stage 3 AI 服务将使用降级策略")

entity_word_service = EntityWordProvider(
    api_key=deepseek_api_key or "",
    api_base=provider_config.get("api_base", "https://api.deepseek.com/v1"),
    prompt_template=entity_word_prompt_template
)

print(f"✅ Stage 3 AI 服务已初始化: entity_word_expert_v1")

# ============ 数据库初始化 ============

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    init_db()

# ============ CORS 配置 ============

# CORS配置 - 生产环境：仅允许指定域名
# 从环境变量读取允许的源，默认为本地开发
ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ 仅允许指定域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ 明确指定方法
    allow_headers=["Content-Type", "Authorization"],  # ✅ 明确指定头部
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

            # 从数据库重新查询带ID的属性词（修复：前端需要数据库ID）
            saved_attributes = crud_attribute.get_attributes_by_task(db, task_id)
            attributes_with_ids = [
                AttributeWithSelection.model_validate(attr).model_dump()
                for attr in saved_attributes
            ]

            # 返回带ID的数据库对象（转换为字典）
            return AttributeResponse(
                concept=request.concept,
                entity_word=request.entity_word,
                attributes=attributes_with_ids,
                task_id=task_id,
                metadata=metadata
            )

        except Exception as db_error:
            # 数据库保存失败 - 这是关键错误，应该抛出异常
            print(f"❌ 数据库保存失败: {str(db_error)}")
            raise HTTPException(status_code=500, detail=f"保存任务失败: {str(db_error)}")
        # ============================================

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


# ============ Stage 3 API: 本体词生成与搜索词组合 ============

@app.post("/api/stage3/tasks/{task_id}/entity-words/generate", response_model=EntityWordGenerateResponse)
async def generate_entity_words(
    task_id: str,
    request: EntityWordGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 3 API 1: 生成本体词变体

    使用 AI 生成本体词的同义词和变体
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 状态前置条件验证
    allowed_statuses = ["selected", "entity_expanded", "entity_selected", "combined"]
    if task.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"当前任务状态不允许生成本体词，请先完成属性词筛选。当前状态: {task.status}"
        )

    # 检查是否已生成本体词
    existing_entity_words = crud_entity_word.get_entity_words_by_task(db, task_id, include_deleted=False)
    if existing_entity_words:
        # 已生成，返回现有数据
        stats = crud_entity_word.get_entity_word_stats(db, task_id)
        entity_word_items = [EntityWordItem.model_validate(ew) for ew in existing_entity_words]

        return EntityWordGenerateResponse(
            task_id=task.task_id,
            entity_words=entity_word_items,
            metadata=EntityWordMetadata(**stats),
            status=task.status,
            updated_at=task.updated_at
        )

    # 生成本体词
    max_count = request.options.max_count if request.options else 15

    try:
        # 调用 AI 服务（带重试和降级策略）
        entity_words = await entity_word_service.generate_entity_words(task.entity_word, max_count)

        # 保存到数据库
        crud_entity_word.create_entity_words_batch(db, task_id, task.concept, entity_words, source="ai")

        # 更新任务状态
        crud_task.update_task_status(db, task_id, "entity_expanded")

        # 获取最新数据
        task = crud_task.get_task(db, task_id)
        entity_words_db = crud_entity_word.get_entity_words_by_task(db, task_id, include_deleted=False)
        stats = crud_entity_word.get_entity_word_stats(db, task_id)

        entity_word_items = [EntityWordItem.model_validate(ew) for ew in entity_words_db]

        return EntityWordGenerateResponse(
            task_id=task.task_id,
            entity_words=entity_word_items,
            metadata=EntityWordMetadata(**stats),
            status=task.status,
            updated_at=task.updated_at
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成本体词失败: {str(e)}")


@app.get("/api/stage3/tasks/{task_id}/entity-words", response_model=EntityWordListResponse)
async def get_entity_words(
    task_id: str,
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    """
    Stage 3 API 2: 查询本体词列表
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 查询本体词
    entity_words = crud_entity_word.get_entity_words_by_task(db, task_id, include_deleted)

    if not entity_words:
        raise HTTPException(status_code=404, detail="未生成本体词，请先调用生成接口")

    stats = crud_entity_word.get_entity_word_stats(db, task_id)
    entity_word_items = [EntityWordItem.model_validate(ew) for ew in entity_words]

    return EntityWordListResponse(
        task_id=task_id,
        entity_words=entity_word_items,
        metadata=EntityWordMetadata(**stats)
    )


@app.put("/api/stage3/tasks/{task_id}/entity-words/selection", response_model=EntityWordSelectionResponse)
async def update_entity_word_selection(
    task_id: str,
    request: EntityWordSelectionRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 3 API 3: 更新本体词选择

    保存用户的选择，包括：
    - 勾选/取消勾选本体词
    - 添加自定义本体词
    - 删除本体词（软删除 + 级联删除相关搜索词）
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 空选择验证
    current_selected_count = len(request.selected_entity_word_ids)
    new_count = len(request.new_entity_words)

    if current_selected_count == 0 and new_count == 0:
        raise HTTPException(
            status_code=400,
            detail="至少需要选择 1 个本体词或添加 1 个自定义本体词"
        )

    # 转换自定义本体词为标准格式
    new_entity_words_data = []
    for new_ew in request.new_entity_words:
        new_entity_words_data.append({
            "entity_word": new_ew.entity_word,
            "type": "original",
            "translation": f"{new_ew.entity_word}（用户添加）",
            "use_case": "用户自定义",
            "recommended": True,
            "search_value": "high",
            "search_value_stars": 5
        })

    try:
        # 更新选择（包括级联软删除）
        selected_count, added_count, deleted_count = crud_entity_word.update_entity_word_selection(
            db,
            task_id,
            request.selected_entity_word_ids,
            new_entity_words_data,
            request.deleted_entity_word_ids,
            task.concept
        )

        # 更新任务状态
        crud_task.update_task_status(db, task_id, "entity_selected")

        # 获取最新数据
        task = crud_task.get_task(db, task_id)
        total_count = len(crud_entity_word.get_entity_words_by_task(db, task_id, include_deleted=False))

        return EntityWordSelectionResponse(
            task_id=task.task_id,
            status=task.status,
            updated_at=task.updated_at,
            metadata={
                "selected_count": selected_count,
                "total_count": total_count,
                "changes": {
                    "selected": len(request.selected_entity_word_ids),
                    "added": added_count,
                    "deleted": deleted_count
                }
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新选择失败: {str(e)}")


@app.post("/api/stage3/tasks/{task_id}/search-terms", response_model=SearchTermGenerateResponse)
async def generate_search_terms(
    task_id: str,
    request: SearchTermGenerateRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 3 API 4: 生成搜索词组合

    笛卡尔积组合：属性词 × 本体词
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 状态前置条件验证
    allowed_statuses = ["entity_selected", "combined"]
    if task.status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"当前任务状态不允许生成搜索词，请先完成本体词筛选。当前状态: {task.status}"
        )

    # 获取选中的属性词和本体词
    selected_attributes = crud_attribute.get_selected_attributes(db, task_id)
    selected_entity_words = crud_entity_word.get_selected_entity_words(db, task_id)

    if not selected_attributes:
        raise HTTPException(status_code=400, detail="没有选中的属性词，请先选择属性词")

    if not selected_entity_words:
        raise HTTPException(status_code=400, detail="没有选中的本体词，请先选择本体词")

    # 笛卡尔积上限验证
    attr_count = len(selected_attributes)
    entity_count = len(selected_entity_words)
    total_combinations = attr_count * entity_count

    MAX_SEARCH_TERMS = 1000
    if total_combinations > MAX_SEARCH_TERMS:
        raise HTTPException(
            status_code=400,
            detail=f"搜索词组合数量超过上限（当前：{attr_count} × {entity_count} = {total_combinations}，上限：{MAX_SEARCH_TERMS}），请减少属性词或本体词的选择数量"
        )

    # 获取选项
    max_length = request.options.max_length if request.options else 80

    try:
        # 幂等操作：删除现有搜索词
        crud_search_term.delete_existing_search_terms(db, task_id)

        # 笛卡尔积组合
        search_terms_data = []
        for attr in selected_attributes:
            for entity in selected_entity_words:
                term = f"{attr.word} {entity.entity_word}"
                length = len(term)
                is_valid = length <= max_length

                search_terms_data.append({
                    "term": term,
                    "attribute_id": attr.id,
                    "attribute_word": attr.word,
                    "entity_word_id": entity.id,
                    "entity_word": entity.entity_word,
                    "length": length,
                    "is_valid": is_valid
                })

        # 批量保存
        crud_search_term.create_search_terms_batch(db, task_id, search_terms_data)

        # 更新任务状态
        crud_task.update_task_status(db, task_id, "combined")

        # 获取最新数据
        task = crud_task.get_task(db, task_id)
        search_terms, total = crud_search_term.get_search_terms_by_task(
            db, task_id, page=1, page_size=total_combinations
        )
        stats = crud_search_term.get_search_term_stats(db, task_id)

        search_term_items = [SearchTermItem.model_validate(st) for st in search_terms]

        return SearchTermGenerateResponse(
            task_id=task.task_id,
            search_terms=search_term_items,
            metadata=SearchTermMetadata(
                total_terms=stats["total_terms"],
                valid_terms=stats["valid_terms"],
                invalid_terms=stats["invalid_terms"],
                attribute_count=attr_count,
                entity_word_count=entity_count
            ),
            status=task.status,
            updated_at=task.updated_at
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成搜索词失败: {str(e)}")


@app.get("/api/stage3/tasks/{task_id}/search-terms", response_model=SearchTermListResponse)
async def get_search_terms(
    task_id: str,
    page: int = 1,
    page_size: int = 20,
    filter_by_attribute: str = None,
    filter_by_entity: str = None,
    include_deleted: bool = False,
    db: Session = Depends(get_db)
):
    """
    Stage 3 API 5: 查询搜索词列表（分页）
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    # 查询搜索词
    search_terms, total = crud_search_term.get_search_terms_by_task(
        db, task_id, page, page_size, filter_by_attribute, filter_by_entity, include_deleted
    )

    search_term_items = [SearchTermItem.model_validate(st) for st in search_terms]

    return SearchTermListResponse(
        task_id=task_id,
        search_terms=search_term_items,
        total=total,
        page=page,
        page_size=page_size,
        filter_by_attribute=filter_by_attribute,
        filter_by_entity=filter_by_entity
    )


@app.delete("/api/stage3/tasks/{task_id}/search-terms/batch", response_model=SearchTermBatchDeleteResponse)
async def batch_delete_search_terms(
    task_id: str,
    request: SearchTermBatchDeleteRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 3 API 6: 批量删除搜索词（软删除）
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {task_id}")

    try:
        # 批量软删除（带原子性验证）
        deleted_count = crud_search_term.soft_delete_search_terms(
            db, task_id, request.search_term_ids
        )

        # 获取剩余数量
        remaining_count = crud_search_term.get_remaining_count(db, task_id)

        return SearchTermBatchDeleteResponse(
            task_id=task_id,
            deleted_count=deleted_count,
            remaining_count=remaining_count,
            message=f"已成功删除 {deleted_count} 个搜索词"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除搜索词失败: {str(e)}")


# ============================================
# Stage 4: Bulksheet 导出
# ============================================

@app.post("/api/stage4/save-product-info", response_model=ProductInfoResponse)
async def save_product_info(
    request: ProductInfoRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 4 API 1: 保存产品信息（SKU, ASIN, Model）
    """
    # 检查任务是否存在
    task = crud_task.get_task(db, request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {request.task_id}")

    try:
        # 更新产品信息
        updated_task = crud_task.update_product_info(
            db=db,
            task_id=request.task_id,
            sku=request.sku,
            asin=request.asin,
            model=request.model.value  # Enum to string
        )

        return ProductInfoResponse(
            task_id=updated_task.task_id,
            product_info=ProductInfo(
                sku=updated_task.sku,
                asin=updated_task.asin,
                model=updated_task.model
            ),
            saved_at=datetime.utcnow().isoformat() + "Z"
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存产品信息失败: {str(e)}")


@app.post("/api/stage4/export")
async def export_bulksheet(
    request: ExportRequest,
    db: Session = Depends(get_db)
):
    """
    Stage 4 API 2: 导出 Bulksheet Excel 文件
    """
    # 1. 检查任务是否存在
    task = crud_task.get_task(db, request.task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"任务不存在: {request.task_id}")

    # 2. 检查产品信息是否已保存
    product_info = crud_task.get_product_info(db, request.task_id)
    if not product_info:
        raise HTTPException(
            status_code=400,
            detail="产品信息未保存，请先调用 /api/stage4/save-product-info"
        )

    # 3. 获取有效搜索词
    search_terms = crud_search_term.get_valid_search_terms(db, request.task_id)
    if not search_terms:
        raise HTTPException(
            status_code=400,
            detail="没有可导出的搜索词，请先完成 Stage 3"
        )

    # 4. 获取本体词（用于 Campaign Negative Keywords）
    entity_words = crud_entity_word.get_all_entity_words(db, request.task_id)

    try:
        # 5. 生成 Bulksheet
        from app.services.bulksheet_generator import BulksheetGenerator

        budget_info = {
            "daily_budget": request.daily_budget,
            "ad_group_default_bid": request.ad_group_default_bid,
            "keyword_bid": request.keyword_bid
        }

        generator = BulksheetGenerator(
            task=task,
            product_info=product_info,
            budget_info=budget_info
        )

        # 生成 Excel 文件到内存
        excel_buffer = generator.generate_excel(search_terms, entity_words)

        # 生成文件名
        filename = generator.generate_filename()

        # 6. 返回文件流
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成 Bulksheet 失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

"""
Bulksheet SaaS - Minimal FastAPI Application
采用TDD方式，从最简单的功能开始
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from datetime import datetime
import uuid

from app.models import (
    AttributeRequest,
    AttributeResponse,
    AttributeWord,
    AttributeMetadata
)
from app.config import load_prompt, load_ai_config
from app.services.deepseek_provider import DeepSeekProvider

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
async def generate_attribute_candidates(request: AttributeRequest):
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

        return AttributeResponse(
            concept=request.concept,
            entity_word=request.entity_word,
            attributes=attributes,
            task_id=task_id,
            metadata=metadata
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成属性词失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

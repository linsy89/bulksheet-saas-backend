"""
Bulksheet SaaS - Minimal FastAPI Application
采用TDD方式，从最简单的功能开始
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uuid

from app.models import AttributeRequest, AttributeResponse, AttributeCandidate
from app.deepseek_client import generate_attributes

app = FastAPI(
    title="Bulksheet SaaS",
    version="2.0.0",
    description="AI-powered Amazon Advertising Bulksheet Generator"
)

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


# ============ Stage 1: 属性词生成 ============

@app.post("/api/stage1/generate", response_model=AttributeResponse)
async def generate_attribute_candidates(request: AttributeRequest):
    """
    Stage 1: 生成属性词候选

    接收用户输入的属性概念，调用AI生成属性词候选列表
    """
    try:
        # 调用DeepSeek API生成属性词
        attributes_data = await generate_attributes(request.concept)

        # 转换为响应格式
        candidates = [
            AttributeCandidate(word=attr["word"], variants=attr.get("variants", []))
            for attr in attributes_data
        ]

        # 生成任务ID（用于后续阶段跟踪）
        task_id = str(uuid.uuid4())

        return AttributeResponse(
            concept=request.concept,
            candidates=candidates,
            task_id=task_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成属性词失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

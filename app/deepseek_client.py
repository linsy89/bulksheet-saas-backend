"""
DeepSeek API客户端
处理AI生成请求
"""

import os
import aiohttp
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


async def generate_attributes(concept: str) -> List[Dict[str, any]]:
    """
    使用DeepSeek API生成属性词候选

    Args:
        concept: 属性概念（如"ocean", "海洋"）

    Returns:
        属性词列表，例如: [{"word": "ocean", "variants": ["oceanic", "sea"]}, ...]
    """

    # 构建提示词
    prompt = f"""
你是一个Amazon广告关键词专家。

任务：给定一个属性概念"{concept}"，生成5-10个相关的英文属性词及其变体。

要求：
1. 如果输入是中文，先翻译成英文
2. 生成形容词/名词形式的属性词
3. 每个属性词提供2-3个常见变体
4. 适合用于产品描述

输出格式（严格JSON）：
```json
[
  {{"word": "ocean", "variants": ["oceanic", "sea", "marine"]}},
  {{"word": "beach", "variants": ["coastal", "shore", "seaside"]}}
]
```

只输出JSON，不要其他文字。
"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{DEEPSEEK_API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant that generates JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                },
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]

                    # 解析JSON（去除markdown代码块）
                    import json
                    import re
                    # 提取JSON部分
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        content = json_match.group(1)

                    attributes = json.loads(content)
                    return attributes
                else:
                    # API调用失败，返回备用结果
                    return get_fallback_attributes(concept)

    except Exception as e:
        print(f"DeepSeek API错误: {e}")
        return get_fallback_attributes(concept)


def get_fallback_attributes(concept: str) -> List[Dict[str, any]]:
    """
    当API失败时的备用属性生成
    使用规则引擎生成
    """
    # 简单的映射表（生产环境应该更完善）
    fallback_map = {
        "ocean": [
            {"word": "ocean", "variants": ["oceanic", "sea", "marine"]},
            {"word": "beach", "variants": ["coastal", "shore", "seaside"]},
            {"word": "water", "variants": ["aqua", "aquatic", "H2O"]},
            {"word": "blue", "variants": ["navy", "azure", "sapphire"]},
            {"word": "wave", "variants": ["surf", "tide", "current"]}
        ],
        "海洋": [
            {"word": "ocean", "variants": ["oceanic", "sea", "marine"]},
            {"word": "beach", "variants": ["coastal", "shore", "seaside"]},
            {"word": "water", "variants": ["aqua", "aquatic"]},
            {"word": "blue", "variants": ["navy", "azure"]},
        ],
        "cute": [
            {"word": "cute", "variants": ["adorable", "kawaii", "lovely"]},
            {"word": "sweet", "variants": ["darling", "charming"]},
            {"word": "pretty", "variants": ["beautiful", "attractive"]},
        ],
        "teen": [
            {"word": "teen", "variants": ["teenage", "teenager", "teens"]},
            {"word": "youth", "variants": ["young", "youthful"]},
            {"word": "girl", "variants": ["girls", "girly"]},
        ]
    }

    return fallback_map.get(concept.lower(), [
        {"word": concept, "variants": [concept + "s", concept + "y"]}
    ])

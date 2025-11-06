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

    # 构建提示词（基于完整的属性词扩展专家Prompt）
    prompt = f"""
你是亚马逊广告属性词扩展专家。

# 核心概念
**本体词-属性词关系**：
- 本体词：定义"商品是什么"（如 phone case, iphone 16 pro case）
- 属性词：描述"商品什么样"（如 red, cute, protective）
- 完整搜索词 = 本体词 + 属性词

**任务目标**：
给定属性词概念 "{concept}"，扩展生成10-20个可用属性词。

# 语义辐射扩展（三层结构）

**第一层：同义词**（语义重叠度 ≥ 90%）
- 意思几乎完全相同的词
- 可直接相互替换
- 包含单复数、英美拼写差异

**第二层：相近词**（语义相关但有差异）
- 基于语义关联灵活扩展
- 可能的维度（不限于）：概念延伸、场景元素、风格调性、人群细分、功能相关
- 不要对象名词（❌ dolphin, bunny, teddy bear）
- 只要描述性词汇（✅ oceanic, cute, protective）

**第三层：变体**（形式变化）
- 基于原词/同义词的语法变化
- 包括：单复数、介词组合、所有格、词性转换
- 包含常见拼写错误和口语化表达

# 本体词验证（质量闸门）

**验证标准**：每个属性词必须与 "phone case" 组合后：
- ✅ 语法正确（符合英语习惯）
- ✅ 语义合理（是合理的商品描述）
- ✅ 搜索可能（用户可能这样搜索）
- ✅ 商业价值（有搜索和转化潜力）

**示例**：
- ocean + phone case = ocean phone case ✅（海洋主题手机壳）
- beach + phone case = beach phone case ✅（海滩主题手机壳）
- dolphin + phone case = dolphin phone case ❌（对象名词，不是属性）

# 严格要求

1. **数量**：必须生成10-20个属性词
2. **类型**：必须包含同义词、相近词、变体三种类型
3. **验证**：每个词都必须与本体词组合验证
4. **语言**：如果输入是中文，输出英文属性词
5. **质量**：不要对象名词，只要形容词和描述性词汇

# 输出格式（严格JSON）

```json
[
  {{
    "word": "ocean",
    "type": "原词",
    "variants": ["oceanic", "sea", "marine"]
  }},
  {{
    "word": "beach",
    "type": "相近词",
    "variants": ["coastal", "shore", "seaside"]
  }},
  {{
    "word": "nautical",
    "type": "相近词",
    "variants": ["maritime", "naval", "seafaring"]
  }}
]
```

**关键**：
- word: 主属性词（英文小写）
- type: 词汇类型（原词/同义词/相近词/变体）
- variants: 2-4个变体词

只输出JSON数组，不要任何其他文字、标题、说明。
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

                    # 兼容处理：如果返回的JSON包含type字段，转换为简化格式
                    # 保持与前端的兼容性
                    simplified = []
                    for attr in attributes:
                        simplified.append({
                            "word": attr.get("word", ""),
                            "variants": attr.get("variants", [])
                        })

                    return simplified
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

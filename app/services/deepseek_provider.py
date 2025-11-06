"""
DeepSeek AI 提供商实现
"""

import os
import json
import re
import aiohttp
import traceback
from typing import List, Dict
from .ai_service import AIService


class DeepSeekProvider(AIService):
    """DeepSeek API 服务提供商"""

    def __init__(self, config: dict, prompt_template: str):
        """
        初始化 DeepSeek 提供商

        Args:
            config: 配置字典（包含 api_key_env, api_base, model 等）
            prompt_template: 提示词模板（包含 {concept} 占位符）
        """
        self.config = config
        self.prompt_template = prompt_template

        # 从环境变量加载 API Key
        api_key_env = config.get("api_key_env", "DEEPSEEK_API_KEY")
        self.api_key = os.getenv(api_key_env)

        # API 配置
        self.api_base = config.get("api_base", "https://api.deepseek.com/v1")
        self.model = config.get("model", "deepseek-chat")
        self.max_tokens = config.get("max_tokens", 4000)
        self.timeout = config.get("timeout", 90)
        self.temperature = config.get("temperature", 0.7)

    async def generate_attributes(self, concept: str, entity_word: str = "phone case") -> List[Dict]:
        """
        使用 DeepSeek API 生成属性词

        Args:
            concept: 属性概念
            entity_word: 本体词

        Returns:
            属性词列表（中文字段）
        """
        try:
            # 检查 API Key
            if not self.api_key:
                print("❌ 错误：DEEPSEEK_API_KEY 未配置")
                return self._get_fallback_attributes(concept)

            # 填充提示词模板
            prompt = self.prompt_template.format(concept=concept)

            print(f"🔵 调用 DeepSeek API，概念: {concept}")

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are a helpful assistant that generates JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response:
                    print(f"🔵 DeepSeek API 响应状态码: {response.status}")

                    if response.status == 200:
                        data = await response.json()
                        print(f"🔵 API 返回数据结构: {list(data.keys())}")

                        content = data["choices"][0]["message"]["content"]
                        print(f"🔵 AI 返回内容前100字符: {content[:100]}...")

                        # 解析 JSON（去除 markdown 代码块）
                        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                        if json_match:
                            content = json_match.group(1)
                            print(f"🔵 提取JSON代码块成功")
                        else:
                            print(f"⚠️  未找到JSON代码块，直接解析内容")

                        attributes = json.loads(content)
                        print(f"✅ 成功解析JSON，属性词数量: {len(attributes)}")

                        return attributes
                    else:
                        # API 调用失败，返回备用结果
                        error_text = await response.text()
                        print(f"❌ API返回错误状态码 {response.status}: {error_text[:200]}")
                        return self._get_fallback_attributes(concept)

        except Exception as e:
            print(f"❌ DeepSeek API错误: {type(e).__name__}: {str(e)}")
            print(f"❌ 错误堆栈: {traceback.format_exc()}")
            return self._get_fallback_attributes(concept)

    def _get_fallback_attributes(self, concept: str) -> List[Dict]:
        """
        当 API 失败时的备用属性生成

        Args:
            concept: 属性概念

        Returns:
            备用属性词列表
        """
        fallback_map = {
            "ocean": [
                {
                    "序号": 1,
                    "原始属性词概念": concept,
                    "属性词": "ocean",
                    "词汇类型": "原词",
                    "中文翻译说明": "海洋、大海",
                    "适用场景": "海洋主题产品",
                    "搜索价值": "⭐⭐⭐⭐⭐ 高",
                    "推荐度": "✅"
                },
                {
                    "序号": 2,
                    "原始属性词概念": concept,
                    "属性词": "oceanic",
                    "词汇类型": "同义词",
                    "中文翻译说明": "海洋的、大洋的",
                    "适用场景": "海洋主题产品",
                    "搜索价值": "⭐⭐⭐⭐ 中高",
                    "推荐度": "✅"
                }
            ],
            "cute": [
                {
                    "序号": 1,
                    "原始属性词概念": concept,
                    "属性词": "cute",
                    "词汇类型": "原词",
                    "中文翻译说明": "可爱的",
                    "适用场景": "可爱风格产品",
                    "搜索价值": "⭐⭐⭐⭐⭐ 高",
                    "推荐度": "✅"
                },
                {
                    "序号": 2,
                    "原始属性词概念": concept,
                    "属性词": "adorable",
                    "词汇类型": "同义词",
                    "中文翻译说明": "讨人喜欢的、可爱的",
                    "适用场景": "可爱风格产品",
                    "搜索价值": "⭐⭐⭐⭐ 中高",
                    "推荐度": "✅"
                }
            ]
        }

        # 默认返回格式
        default_result = [
            {
                "序号": 1,
                "原始属性词概念": concept,
                "属性词": concept,
                "词汇类型": "原词",
                "中文翻译说明": f"备用结果: {concept}",
                "适用场景": "通用场景",
                "搜索价值": "⭐⭐⭐ 中",
                "推荐度": "⚠️"
            }
        ]

        return fallback_map.get(concept.lower(), default_result)

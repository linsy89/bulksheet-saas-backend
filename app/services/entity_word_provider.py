"""
本体词生成服务
使用 DeepSeek API 生成本体词的同义词和变体
"""

import json
import re
import logging
from typing import List, Dict, Tuple
from json.decoder import JSONDecodeError
from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log
from app.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)


def validate_entity_word(entity_word: str) -> Tuple[bool, str]:
    """
    验证本体词格式

    Args:
        entity_word: 本体词文本

    Returns:
        (is_valid, error_message)
    """
    # 规则1: 长度验证
    if len(entity_word) > 200:
        return False, "本体词长度不能超过 200 个字符"

    if len(entity_word.strip()) == 0:
        return False, "本体词不能为空"

    # 规则2: 字符验证（只允许英文、数字、空格、连字符）
    pattern = r'^[a-zA-Z0-9\s\-]+$'
    if not re.match(pattern, entity_word):
        return False, "本体词只能包含英文字母、数字、空格和连字符"

    # 规则3: 不允许连续多个空格
    if "  " in entity_word:
        return False, "本体词不能包含连续空格"

    return True, ""


def convert_entity_word_to_standard(entity_word_data: Dict) -> Dict:
    """
    转换 AI 返回的本体词数据为标准格式

    输入（中文字段）:
    {
        "本体词": "iphone 14 case",
        "词汇类型": "原词",
        "中文说明": "...",
        "适用场景": "...",
        "推荐度": "✅",
        "搜索价值": "⭐⭐⭐⭐⭐"
    }

    输出（英文字段）:
    {
        "entity_word": "iphone 14 case",
        "type": "original",
        "translation": "...",
        "use_case": "...",
        "recommended": true,
        "search_value": "high",
        "search_value_stars": 5
    }
    """
    # 类型映射
    type_mapping = {
        "原词": "original",
        "同义词": "synonym",
        "变体": "variant"
    }

    # 推荐度转换
    recommended = entity_word_data.get("推荐度", "✅") == "✅"

    # 搜索价值转换
    stars_count = entity_word_data.get("搜索价值", "⭐⭐⭐").count("⭐")
    if stars_count >= 4:
        search_value = "high"
    elif stars_count == 3:
        search_value = "medium"
    else:
        search_value = "low"

    return {
        "entity_word": entity_word_data.get("本体词", ""),
        "type": type_mapping.get(entity_word_data.get("词汇类型", "原词"), "original"),
        "translation": entity_word_data.get("中文说明", ""),
        "use_case": entity_word_data.get("适用场景", ""),
        "recommended": recommended,
        "search_value": search_value,
        "search_value_stars": stars_count
    }


class InsufficientResultsError(Exception):
    """AI 返回结果不足"""
    pass


class EntityWordProvider:
    """本体词生成服务提供者"""

    def __init__(self, deepseek_client: DeepSeekClient, prompt_template: str):
        self.client = deepseek_client
        self.prompt_template = prompt_template

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.INFO),
        reraise=True
    )
    async def _call_api(self, prompt: str) -> str:
        """
        调用 DeepSeek API（带重试）

        重试条件：
        - TimeoutError（超时）
        - ConnectionError（连接失败）
        - Exception（其他异常）

        不重试条件：
        - 无（所有异常都会重试）
        """
        logger.info(f"调用 DeepSeek API 生成本体词...")
        response = await self.client.generate(prompt, temperature=0.7)
        logger.info(f"API 调用成功，返回长度: {len(response)}")
        return response

    def _parse_response(self, response: str) -> List[Dict]:
        """
        解析 AI 响应（处理 JSON 和 markdown 代码块）
        """
        # 尝试直接解析 JSON
        try:
            data = json.loads(response)
            if isinstance(data, list):
                return data
        except JSONDecodeError:
            pass

        # 尝试提取 markdown 代码块中的 JSON
        json_pattern = r'```(?:json)?\s*(\[[\s\S]*?\])\s*```'
        matches = re.findall(json_pattern, response)

        if matches:
            try:
                data = json.loads(matches[0])
                if isinstance(data, list):
                    return data
            except JSONDecodeError:
                pass

        # 尝试查找任何 JSON 数组
        array_pattern = r'\[\s*\{[\s\S]*?\}\s*\]'
        matches = re.findall(array_pattern, response)

        if matches:
            try:
                data = json.loads(matches[0])
                if isinstance(data, list):
                    return data
            except JSONDecodeError:
                pass

        raise JSONDecodeError(f"无法解析 AI 响应为 JSON: {response[:200]}", response, 0)

    def _validate_entity_words(self, entity_words: List[Dict], original: str) -> List[Dict]:
        """验证本体词质量"""
        valid_words = []

        for ew in entity_words:
            # 检查必填字段
            if not ew.get("本体词"):
                continue

            # 检查本体词格式
            is_valid, _ = validate_entity_word(ew.get("本体词", ""))
            if not is_valid:
                continue

            valid_words.append(ew)

        return valid_words

    def _get_enhanced_basic_variants(self, entity_word: str) -> List[Dict]:
        """
        生成增强的基础变体（不依赖 AI）
        确保至少返回 5-8 个变体
        """
        variants = []
        words = entity_word.split()

        # 1. 原词（必须）
        variants.append({
            "本体词": entity_word,
            "词汇类型": "原词",
            "中文说明": f"{entity_word}（原始输入）",
            "适用场景": "用户标准搜索词",
            "推荐度": "✅",
            "搜索价值": "⭐⭐⭐⭐⭐"
        })

        # 2. 去空格变体
        if " " in entity_word:
            no_space = entity_word.replace(" ", "")
            variants.append({
                "本体词": no_space,
                "词汇类型": "变体",
                "中文说明": "去空格变体",
                "适用场景": "用户快速输入",
                "推荐度": "⚠️",
                "搜索价值": "⭐⭐⭐"
            })

        # 3. 单复数变体
        if entity_word.endswith("s"):
            singular = entity_word[:-1]
            variants.append({
                "本体词": singular,
                "词汇类型": "变体",
                "中文说明": "单数形式",
                "适用场景": "用户搜索单个商品",
                "推荐度": "✅",
                "搜索价值": "⭐⭐⭐"
            })
        else:
            plural = entity_word + "s"
            variants.append({
                "本体词": plural,
                "词汇类型": "变体",
                "中文说明": "复数形式",
                "适用场景": "用户搜索多个商品",
                "推荐度": "✅",
                "搜索价值": "⭐⭐⭐"
            })

        # 4. 连字符变体
        if " " in entity_word:
            hyphen_variant = entity_word.replace(" ", "-")
            variants.append({
                "本体词": hyphen_variant,
                "词汇类型": "变体",
                "中文说明": "连字符形式",
                "适用场景": "某些平台的搜索习惯",
                "推荐度": "⚠️",
                "搜索价值": "⭐⭐"
            })

        # 5. 词序调整（介词组合）
        if len(words) >= 2:
            last_word = words[-1]
            rest = " ".join(words[:-1])
            reordered = f"{last_word} for {rest}"
            variants.append({
                "本体词": reordered,
                "词汇类型": "变体",
                "中文说明": "介词组合变体",
                "适用场景": "自然语言搜索习惯",
                "推荐度": "✅",
                "搜索价值": "⭐⭐⭐"
            })

        # 6. 缩写变体（如果有数字）
        if any(char.isdigit() for char in entity_word) and len(words) > 1:
            abbreviated = " ".join([w for w in words if any(c.isdigit() for c in w) or w == words[-1]])
            if abbreviated != entity_word:
                variants.append({
                    "本体词": abbreviated,
                    "词汇类型": "变体",
                    "中文说明": "简写形式",
                    "适用场景": "用户省略品牌名",
                    "推荐度": "⚠️",
                    "搜索价值": "⭐⭐"
                })

        # 7. 全小写变体
        if entity_word != entity_word.lower():
            variants.append({
                "本体词": entity_word.lower(),
                "词汇类型": "变体",
                "中文说明": "全小写形式",
                "适用场景": "标准搜索习惯",
                "推荐度": "✅",
                "搜索价值": "⭐⭐⭐"
            })

        return variants

    async def generate_entity_words(self, entity_word: str, max_count: int = 15) -> List[Dict]:
        """
        生成本体词（带降级策略）

        Args:
            entity_word: 原始本体词
            max_count: 最大生成数量

        Returns:
            本体词列表（英文字段格式）
        """
        # 1. 输入验证
        is_valid, error_msg = validate_entity_word(entity_word)
        if not is_valid:
            raise ValueError(error_msg)

        try:
            # 2. 尝试 AI 生成（带重试）
            prompt = self.prompt_template.format(entity_word=entity_word)
            response = await self._call_api(prompt)

            # 3. 解析响应
            entity_words_cn = self._parse_response(response)

            # 4. 验证结果
            entity_words_cn = self._validate_entity_words(entity_words_cn, entity_word)

            # 5. 检查结果数量
            if len(entity_words_cn) < 3:
                logger.warning(f"AI 返回结果不足（{len(entity_words_cn)}），启用增强降级策略")
                raise InsufficientResultsError("AI 返回结果不足")

            # 6. 转换为标准格式
            entity_words = [convert_entity_word_to_standard(ew) for ew in entity_words_cn]

            return entity_words[:max_count]

        except (TimeoutError, ConnectionError, JSONDecodeError, InsufficientResultsError, Exception) as e:
            logger.error(f"AI 生成失败: {type(e).__name__} - {str(e)}")
            logger.info("使用增强降级策略生成基础变体")

            # 降级：返回增强的基础变体
            variants_cn = self._get_enhanced_basic_variants(entity_word)
            variants = [convert_entity_word_to_standard(v) for v in variants_cn]
            return variants[:max_count]

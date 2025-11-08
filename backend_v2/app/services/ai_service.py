"""
AI 服务抽象接口
定义所有 AI 提供商必须实现的接口
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class AIService(ABC):
    """AI 服务抽象基类"""

    @abstractmethod
    async def generate_attributes(self, concept: str, entity_word: str = "phone case") -> List[Dict]:
        """
        生成属性词列表

        Args:
            concept: 属性概念（如 "ocean", "女性"）
            entity_word: 本体词（如 "phone case"）

        Returns:
            属性词列表，每个属性词包含8个字段（中文字段）
        """
        pass

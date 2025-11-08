"""
配置管理模块
负责加载提示词和AI配置
"""

import os
import yaml
from pathlib import Path


def load_prompt(name: str, version: str = "v1") -> str:
    """
    加载提示词文件

    Args:
        name: 提示词名称（如 "attribute_expert"）
        version: 版本号（默认 "v1"）

    Returns:
        提示词文本内容
    """
    config_dir = Path(__file__).parent
    prompt_file = config_dir / "prompts" / f"{name}_{version}.txt"

    if not prompt_file.exists():
        raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")

    with open(prompt_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_ai_config() -> dict:
    """
    加载AI配置文件

    Returns:
        配置字典
    """
    config_dir = Path(__file__).parent
    config_file = config_dir / "ai_config.yaml"

    if not config_file.exists():
        # 返回默认配置
        return get_default_ai_config()

    with open(config_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def get_default_ai_config() -> dict:
    """
    获取默认AI配置（当配置文件不存在时使用）

    Returns:
        默认配置字典
    """
    return {
        "providers": {
            "deepseek": {
                "api_key_env": "DEEPSEEK_API_KEY",
                "api_base": "https://api.deepseek.com/v1",
                "model": "deepseek-chat",
                "max_tokens": 4000,
                "timeout": 90,
                "temperature": 0.7
            }
        },
        "active_provider": "deepseek",
        "prompt_version": "v1"
    }

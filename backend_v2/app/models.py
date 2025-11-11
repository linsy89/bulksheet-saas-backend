"""
数据模型定义
使用Pydantic进行数据验证
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from enum import Enum


# ============ Stage 1: 属性词生成 ============

class AttributeRequest(BaseModel):
    """属性概念输入请求"""
    concept: str = Field(..., min_length=1, max_length=100, description="属性概念，如'ocean', '海洋'")
    entity_word: str = Field(default="phone case", description="本体词，如'phone case', 'iphone 16 pro case'")


class AttributeWord(BaseModel):
    """属性词实体 - 核心数据单元"""
    word: str = Field(..., description="属性词（英文）")
    concept: str = Field(..., description="原始属性词概念（中文/英文）")
    type: Literal["original", "synonym", "related", "variant"] = Field(..., description="词汇类型")
    translation: str = Field(..., description="中文翻译和说明")
    use_case: str = Field(..., description="适用场景描述")
    search_value: Literal["high", "medium", "low"] = Field(..., description="搜索价值")
    search_value_stars: int = Field(..., ge=1, le=5, description="搜索价值星级: 1-5")
    recommended: bool = Field(..., description="是否推荐")


class AttributeMetadata(BaseModel):
    """属性词生成元数据"""
    total_count: int = Field(..., description="属性词总数")
    generated_at: str = Field(..., description="生成时间（ISO 8601）")
    original_count: int = Field(default=0, description="原词数量")
    synonym_count: int = Field(default=0, description="同义词数量")
    related_count: int = Field(default=0, description="相近词数量")
    variant_count: int = Field(default=0, description="变体数量")


class AttributeResponse(BaseModel):
    """Stage 1 属性词生成响应"""
    concept: str = Field(..., description="输入的属性概念")
    entity_word: str = Field(..., description="本体词")
    attributes: List[Dict] = Field(..., description="属性词列表（包含数据库ID）")
    task_id: str = Field(..., description="任务ID")
    metadata: AttributeMetadata = Field(..., description="元数据")


# ============ Stage 4: Bulksheet 导出 ============

class PhoneModel(str, Enum):
    """手机型号枚举"""
    # iPhone 17 系列 (最新款)
    IPHONE_17_PRO_MAX = "iPhone 17 Pro Max"
    IPHONE_17_PRO = "iPhone 17 Pro"
    IPHONE_17_AIR = "iPhone 17 Air"
    IPHONE_17 = "iPhone 17"

    # iPhone 16 系列
    IPHONE_16_PRO_MAX = "iPhone 16 Pro Max"
    IPHONE_16_PRO = "iPhone 16 Pro"
    IPHONE_16_PLUS = "iPhone 16 Plus"
    IPHONE_16 = "iPhone 16"

    # iPhone 15 系列
    IPHONE_15_PRO_MAX = "iPhone 15 Pro Max"
    IPHONE_15_PRO = "iPhone 15 Pro"
    IPHONE_15_PLUS = "iPhone 15 Plus"
    IPHONE_15 = "iPhone 15"

    # iPhone 14 系列
    IPHONE_14_PRO_MAX = "iPhone 14 Pro Max"
    IPHONE_14_PRO = "iPhone 14 Pro"
    IPHONE_14_PLUS = "iPhone 14 Plus"
    IPHONE_14 = "iPhone 14"

    # iPhone 13 系列
    IPHONE_13_PRO_MAX = "iPhone 13 Pro Max"
    IPHONE_13_PRO = "iPhone 13 Pro"
    IPHONE_13 = "iPhone 13"
    IPHONE_13_MINI = "iPhone 13 mini"

    # iPhone 12 系列
    IPHONE_12_PRO_MAX = "iPhone 12 Pro Max"
    IPHONE_12_PRO = "iPhone 12 Pro"
    IPHONE_12 = "iPhone 12"
    IPHONE_12_MINI = "iPhone 12 mini"

    # iPhone 11 系列
    IPHONE_11_PRO_MAX = "iPhone 11 Pro Max"
    IPHONE_11_PRO = "iPhone 11 Pro"
    IPHONE_11 = "iPhone 11"

    # iPhone SE 系列
    IPHONE_SE_2022 = "iPhone SE (2022)"
    IPHONE_SE_2020 = "iPhone SE (2020)"

    # iPhone XS/XR 系列
    IPHONE_XS_MAX = "iPhone XS Max"
    IPHONE_XS = "iPhone XS"
    IPHONE_XR = "iPhone XR"


class ProductInfoRequest(BaseModel):
    """保存产品信息请求"""
    task_id: str = Field(..., description="任务ID")
    sku: str = Field(..., min_length=1, max_length=100, description="产品SKU")
    asin: str = Field(..., min_length=10, max_length=10, description="亚马逊ASIN（10位）")
    model: PhoneModel = Field(..., description="手机型号")


class ProductInfo(BaseModel):
    """产品信息"""
    sku: str
    asin: str
    model: str


class ProductInfoResponse(BaseModel):
    """保存产品信息响应"""
    task_id: str
    product_info: ProductInfo
    saved_at: str = Field(..., description="保存时间（ISO 8601）")


class ExportFormat(str, Enum):
    """导出格式枚举"""
    XLSX = "xlsx"


class ExportRequest(BaseModel):
    """导出 Bulksheet 请求"""
    task_id: str = Field(..., description="任务ID")
    daily_budget: float = Field(..., gt=0, description="每日预算（美元）")
    ad_group_default_bid: float = Field(..., gt=0, description="广告组默认出价（美元）")
    keyword_bid: float = Field(..., gt=0, description="关键词出价（美元）")
    format: ExportFormat = Field(default=ExportFormat.XLSX, description="导出格式")

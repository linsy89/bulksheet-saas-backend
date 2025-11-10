"""
Bulksheet生成服务
生成符合Amazon Advertising规范的Bulksheet Excel文件
"""

import openpyxl
from io import BytesIO
from typing import List, Dict
from datetime import datetime
from app.models_db import Task, SearchTerm, EntityWord


class BulksheetGenerator:
    """亚马逊 Bulksheet 生成器"""

    # 31列列名（严格顺序）
    COLUMNS = [
        "Product", "Entity", "Operation", "Campaign ID", "Ad Group ID",
        "Portfolio ID", "Ad ID", "Keyword ID", "Product Targeting ID",
        "Campaign Name", "Ad Group Name", "Start Date", "End Date",
        "Targeting Type", "State", "Daily Budget", "SKU", "ASIN",
        "Ad Group Default Bid", "Bid", "Keyword Text",
        "Native Language Keyword", "Native Language Locale",
        "Match Type", "Bidding Strategy", "Placement", "Percentage",
        "Product Targeting Expression", "Audience ID",
        "Shopper Cohort Percentage", "Shopper Cohort Type"
    ]

    def __init__(self, task: Task, product_info: dict, budget_info: dict):
        """
        Args:
            task: Task 对象（包含 concept）
            product_info: {sku, asin, model}
            budget_info: {daily_budget, ad_group_default_bid, keyword_bid}
        """
        self.task = task
        self.product_info = product_info
        self.budget_info = budget_info
        self.campaign_name = self._generate_campaign_name()
        self.ad_group_name = self._generate_ad_group_name()

    def generate_excel(
        self,
        search_terms: List[SearchTerm],
        entity_words: List[EntityWord]
    ) -> BytesIO:
        """生成 Excel 文件到内存"""
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Bulksheet"

        # 1. 写入表头
        sheet.append(self.COLUMNS)

        # 2. 写入 Campaign 行
        sheet.append(self._create_campaign_row())

        # 3. 写入 Ad Group 行
        sheet.append(self._create_ad_group_row())

        # 4. 写入 Product Ad 行
        sheet.append(self._create_product_ad_row())

        # 5. 写入 Keyword 行（Broad match）
        for st in search_terms:
            sheet.append(self._create_keyword_row(st.term))

        # 6. 写入 Campaign Negative Keyword 行（Campaign Negative Exact）
        for ew in entity_words:
            sheet.append(self._create_campaign_negative_keyword_row(ew.entity_word))

        # 保存到内存
        buffer = BytesIO()
        workbook.save(buffer)
        buffer.seek(0)

        return buffer

    def _create_campaign_row(self) -> list:
        """创建 Campaign 行（31个元素的列表）

        注意：基于成功案例 - Campaign ID 和 Campaign Name 都填写
        """
        row = [""] * 31
        row[0] = "Sponsored Products"  # Product
        row[1] = "Campaign"             # Entity
        row[2] = "create"               # Operation
        row[3] = self.campaign_name     # Campaign ID - 填写Campaign Name！
        row[9] = self.campaign_name     # Campaign Name
        row[13] = "Manual"              # Targeting Type
        row[14] = "enabled"             # State
        row[15] = self.budget_info["daily_budget"]  # Daily Budget
        return row

    def _create_ad_group_row(self) -> list:
        """创建 Ad Group 行

        注意：基于成功案例 - 所有4列都填写（ID和Name都填）
        """
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Ad Group"
        row[2] = "create"
        row[3] = self.campaign_name     # Campaign ID
        row[4] = self.ad_group_name     # Ad Group ID
        row[9] = self.campaign_name     # Campaign Name
        row[10] = self.ad_group_name    # Ad Group Name
        row[13] = "Manual"
        row[14] = "enabled"
        row[18] = self.budget_info["ad_group_default_bid"]
        return row

    def _create_product_ad_row(self) -> list:
        """创建 Product Ad 行

        注意：基于成功案例 - 所有4列都填写（ID和Name都填）
        """
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Product Ad"
        row[2] = "create"
        row[3] = self.campaign_name     # Campaign ID
        row[4] = self.ad_group_name     # Ad Group ID
        row[9] = self.campaign_name     # Campaign Name
        row[10] = self.ad_group_name    # Ad Group Name
        row[13] = "Manual"
        row[14] = "enabled"
        row[16] = self.product_info["sku"]   # SKU
        row[17] = self.product_info["asin"]  # ASIN
        return row

    def _create_keyword_row(self, keyword_text: str) -> list:
        """创建 Keyword 行（Broad match）

        注意：基于成功案例 - 所有4列都填写（ID和Name都填）
        """
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Keyword"
        row[2] = "create"
        row[3] = self.campaign_name     # Campaign ID
        row[4] = self.ad_group_name     # Ad Group ID
        row[9] = self.campaign_name     # Campaign Name
        row[10] = self.ad_group_name    # Ad Group Name
        row[14] = "enabled"
        row[19] = self.budget_info["keyword_bid"]  # Bid
        row[20] = keyword_text                      # Keyword Text
        row[23] = "Broad"                           # Match Type (大写B)
        return row

    def _create_campaign_negative_keyword_row(self, keyword_text: str) -> list:
        """创建 Campaign Negative Keyword 行（Campaign Negative Exact）

        注意：
        1. Campaign级别的negative keywords不关联ad group
        2. 基于成功案例 - Campaign ID 和 Campaign Name 都填写
        """
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Keyword"
        row[2] = "create"
        row[3] = self.campaign_name     # Campaign ID
        # row[4] = Ad Group ID - Campaign级别不需要，留空
        row[9] = self.campaign_name     # Campaign Name
        # row[10] = Ad Group Name - Campaign级别不需要，留空
        row[14] = "enabled"
        # row[19] = Bid 留空（negative keyword 不需要出价）
        row[20] = keyword_text                  # Keyword Text
        row[23] = "Campaign Negative Exact"     # Match Type (Campaign级别)
        return row

    def _generate_campaign_name(self) -> str:
        """生成 Campaign Name"""
        return f"{self.product_info['sku']} {self.task.concept} {self.product_info['model']}"

    def _generate_ad_group_name(self) -> str:
        """生成 Ad Group Name"""
        return f"{self.task.concept} {self.product_info['model']}"

    def generate_filename(self) -> str:
        """
        生成文件名
        格式：bulksheet_{campaign_name}_{timestamp}.xlsx
        """
        # 将 campaign_name 中的空格替换为下划线
        safe_campaign_name = self.campaign_name.replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"bulksheet_{safe_campaign_name}_{timestamp}.xlsx"

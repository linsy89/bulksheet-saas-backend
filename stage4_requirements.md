# Stage 4 - Bulksheet 导出功能需求与技术方案

**版本**: v1.1
**创建日期**: 2025-11-07
**最后更新**: 2025-11-07
**状态**: 待开发

**修订记录**：
- v1.1 (2025-11-07): 根据Amazon官方Bulksheet规范验证，修正Match Type大小写和Negative Keywords层级逻辑
- v1.0 (2025-11-07): 初始版本

---

## 目录

- [1. 需求概述](#1-需求概述)
- [2. 业务需求](#2-业务需求)
- [3. 功能设计](#3-功能设计)
- [4. 技术方案](#4-技术方案)
- [5. API 设计](#5-api-设计)
- [6. 数据库设计](#6-数据库设计)
- [7. 实施计划](#7-实施计划)

---

## 1. 需求概述

### 1.1 功能目标

将 Stage 3 生成的搜索词导出为符合亚马逊广告规范的 Bulksheet Excel 文件，支持用户直接上传到亚马逊广告后台进行批量创建广告活动。

### 1.2 核心价值

- **标准化导出**：严格遵循亚马逊 Bulksheet 格式（31列完整结构）
- **一键导出**：自动生成 Campaign、Ad Group、Product Ad、Keyword 四层结构
- **智能过滤**：只导出有效搜索词（is_valid=True）
- **负面关键词**：自动添加本体词变体作为 Campaign Negative Exact 关键词（campaign级别）

### 1.3 参考模版

基于真实亚马逊 Bulksheet 模版：
```
/Users/linshaoyong/Desktop/词根分析2/Flower-BlueFloral2/bluefloral Bulksheets/
Flower-BlueFloral2-IP16PM/Bulksheet_Flower-BlueFloral2-IP16PM_blue_20251023_135611.xlsx
```

---

## 2. 业务需求

### 2.1 导出范围

**搜索词来源**：
- 从 `search_terms` 表读取
- 条件：`task_id` 匹配 AND `is_valid = TRUE` AND `is_deleted = FALSE`

**本体词变体（Campaign Negative Keyword）**：
- 从 `entity_words` 表读取
- 条件：`task_id` 匹配 AND `is_deleted = FALSE`
- 用途：作为 Campaign Negative Exact 关键词（campaign级别，不关联ad group）

### 2.2 命名规则

#### Campaign Name（自动生成）
```
格式：{sku} {concept} {model}
示例：Flower-BlueFloral2-IP16PM blue iPhone 16 Pro Max
```

#### Ad Group Name（自动生成）
```
格式：{concept} {model}
示例：blue iPhone 16 Pro Max
```

**说明**：
- `sku`：产品SKU（用户输入）
- `concept`：属性词概念（从 Task 表读取）
- `model`：手机型号（用户从下拉选项选择）

### 2.3 手机型号选项

固定下拉选项（12个）：
- iPhone 16 Pro Max
- iPhone 16 Pro
- iPhone 16 Plus
- iPhone 16
- iPhone 15 Pro Max
- iPhone 15 Pro
- iPhone 15 Plus
- iPhone 15
- iPhone 14 Pro Max
- iPhone 14 Pro
- iPhone 14 Plus
- iPhone 14

### 2.4 用户输入信息

分两步输入：

#### 步骤1：保存产品信息（一次性）
- SKU：产品SKU码
- ASIN：亚马逊产品ID
- Model：手机型号（从下拉选项选择）

#### 步骤2：导出时输入（每次导出）
- Daily Budget：每日预算（美元）
- Ad Group Default Bid：广告组默认出价（美元）
- Keyword Bid：关键词出价（美元）

---

## 3. 功能设计

### 3.1 Bulksheet 结构

#### 文件格式
- **格式**：Excel (.xlsx)
- **Sheet 名称**：Bulksheet
- **列数**：31列（严格按照亚马逊模版顺序）
- **行结构**：

```
Row 1: Campaign 行（1行）
Row 2: Ad Group 行（1行）
Row 3: Product Ad 行（1行）
Row 4-N: Keyword 行（N行，Broad match，来自 search_terms）
Row N+1-M: Campaign Negative Keyword 行（M行，Campaign Negative Exact，来自 entity_words）
```

### 3.2 完整列定义（31列）

| 列号 | 列名 | 说明 |
|-----|------|------|
| 1 | Product | Sponsored Products |
| 2 | Entity | Campaign/Ad Group/Product Ad/Keyword |
| 3 | Operation | create |
| 4 | Campaign ID | 留空（新建） |
| 5 | Ad Group ID | 留空（新建） |
| 6 | Portfolio ID | 留空 |
| 7 | Ad ID | 留空 |
| 8 | Keyword ID | 留空 |
| 9 | Product Targeting ID | 留空 |
| 10 | Campaign Name | 自动生成 |
| 11 | Ad Group Name | 自动生成 |
| 12 | Start Date | 留空 |
| 13 | End Date | 留空 |
| 14 | Targeting Type | Manual |
| 15 | State | enabled |
| 16 | Daily Budget | 用户输入（仅Campaign行） |
| 17 | SKU | 用户输入（仅Product Ad行） |
| 18 | ASIN | 用户输入（仅Product Ad行） |
| 19 | Ad Group Default Bid | 用户输入（仅Ad Group行） |
| 20 | Bid | 用户输入（仅Keyword行） |
| 21 | Keyword Text | 从数据库读取 |
| 22 | Native Language Keyword | 留空 |
| 23 | Native Language Locale | 留空 |
| 24 | Match Type | Broad / Campaign Negative Exact |
| 25 | Bidding Strategy | 留空 |
| 26 | Placement | 留空 |
| 27 | Percentage | 留空 |
| 28 | Product Targeting Expression | 留空 |
| 29 | Audience ID | 留空 |
| 30 | Shopper Cohort Percentage | 留空 |
| 31 | Shopper Cohort Type | 留空 |

### 3.3 各 Entity 行字段填充规则

#### Campaign 行（Row 1）
```python
{
    "Product": "Sponsored Products",
    "Entity": "Campaign",
    "Operation": "create",
    "Campaign ID": "",  # 留空
    "Campaign Name": "{sku} {concept} {model}",
    "Targeting Type": "Manual",
    "State": "enabled",
    "Daily Budget": daily_budget  # 用户输入
}
```

#### Ad Group 行（Row 2）
```python
{
    "Product": "Sponsored Products",
    "Entity": "Ad Group",
    "Operation": "create",
    "Campaign ID": "{sku} {concept} {model}",  # 同Campaign Name
    "Ad Group ID": "",  # 留空
    "Campaign Name": "{sku} {concept} {model}",
    "Ad Group Name": "{concept} {model}",
    "Targeting Type": "Manual",
    "State": "enabled",
    "Ad Group Default Bid": ad_group_default_bid  # 用户输入
}
```

#### Product Ad 行（Row 3）
```python
{
    "Product": "Sponsored Products",
    "Entity": "Product Ad",
    "Operation": "create",
    "Campaign ID": "{sku} {concept} {model}",
    "Ad Group ID": "{concept} {model}",
    "Campaign Name": "{sku} {concept} {model}",
    "Ad Group Name": "{concept} {model}",
    "Targeting Type": "Manual",
    "State": "enabled",
    "SKU": sku,  # 用户输入
    "ASIN": asin  # 用户输入
}
```

#### Keyword 行（Row 4-N，Broad）
```python
{
    "Product": "Sponsored Products",
    "Entity": "Keyword",
    "Operation": "create",
    "Campaign ID": "{sku} {concept} {model}",
    "Ad Group ID": "{concept} {model}",
    "Campaign Name": "{sku} {concept} {model}",
    "Ad Group Name": "{concept} {model}",
    "State": "enabled",
    "Bid": keyword_bid,  # 用户输入
    "Keyword Text": term,  # 从 search_terms 表读取
    "Match Type": "Broad"  # 大写B，符合Amazon规范
}
```

#### Campaign Negative Keyword 行（Row N+1-M，Campaign Negative Exact）
```python
{
    "Product": "Sponsored Products",
    "Entity": "Keyword",
    "Operation": "create",
    "Campaign ID": "{sku} {concept} {model}",
    "Ad Group ID": "",  # ⚠️ 必须留空！Campaign级别的negative keyword不关联ad group
    "Campaign Name": "{sku} {concept} {model}",
    "Ad Group Name": "",  # ⚠️ 必须留空！
    "State": "enabled",
    "Bid": "",  # 留空，negative keyword 不需要出价
    "Keyword Text": entity_word,  # 从 entity_words 表读取
    "Match Type": "Campaign Negative Exact"  # Campaign级别的negative exact
}
```

**说明**：
- Campaign Negative Keywords 作用于整个 campaign，不属于任何特定的 ad group
- 因此 Ad Group ID 和 Ad Group Name 字段**必须留空**
- 这样可以阻止整个 campaign 的所有 ad groups 在这些关键词上触发广告

### 3.4 文件命名规则

```
格式：bulksheet_{campaign_name}_{timestamp}.xlsx
示例：bulksheet_Flower-BlueFloral2-IP16PM_blue_iPhone_16_Pro_Max_20251107_143022.xlsx
```

---

## 4. 技术方案

### 4.1 技术栈

- **Excel 生成**：`openpyxl` (已安装)
- **响应方式**：文件流（Stream Response）
- **文件存储**：内存缓冲区（BytesIO），不落盘

### 4.2 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     API 层 (main.py)                        │
│  - POST /api/stage4/save-product-info                       │
│  - POST /api/stage4/export                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  CRUD 层 (crud/)                            │
│  - update_product_info()                                    │
│  - get_product_info()                                       │
│  - get_valid_search_terms()                                 │
│  - get_entity_words()                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│             Bulksheet 生成服务                               │
│            (services/bulksheet_generator.py)                │
│  - generate_excel()                                         │
│  - _create_campaign_row()                                   │
│  - _create_ad_group_row()                                   │
│  - _create_product_ad_row()                                 │
│  - _create_keyword_rows()                                   │
│  - _create_negative_keyword_rows()                          │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 核心类设计

#### BulksheetGenerator 类

```python
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
        """创建 Campaign 行（31个元素的列表）"""
        row = [""] * 31
        row[0] = "Sponsored Products"  # Product
        row[1] = "Campaign"             # Entity
        row[2] = "create"               # Operation
        row[9] = self.campaign_name     # Campaign Name
        row[13] = "Manual"              # Targeting Type
        row[14] = "enabled"             # State
        row[15] = self.budget_info["daily_budget"]  # Daily Budget
        return row

    def _create_ad_group_row(self) -> list:
        """创建 Ad Group 行"""
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Ad Group"
        row[2] = "create"
        row[3] = self.campaign_name     # Campaign ID
        row[9] = self.campaign_name     # Campaign Name
        row[10] = self.ad_group_name    # Ad Group Name
        row[13] = "Manual"
        row[14] = "enabled"
        row[18] = self.budget_info["ad_group_default_bid"]
        return row

    def _create_product_ad_row(self) -> list:
        """创建 Product Ad 行"""
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Product Ad"
        row[2] = "create"
        row[3] = self.campaign_name
        row[4] = self.ad_group_name
        row[9] = self.campaign_name
        row[10] = self.ad_group_name
        row[13] = "Manual"
        row[14] = "enabled"
        row[16] = self.product_info["sku"]   # SKU
        row[17] = self.product_info["asin"]  # ASIN
        return row

    def _create_keyword_row(self, keyword_text: str) -> list:
        """创建 Keyword 行（Broad match）"""
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Keyword"
        row[2] = "create"
        row[3] = self.campaign_name
        row[4] = self.ad_group_name
        row[9] = self.campaign_name
        row[10] = self.ad_group_name
        row[14] = "enabled"
        row[19] = self.budget_info["keyword_bid"]  # Bid
        row[20] = keyword_text                      # Keyword Text
        row[23] = "Broad"                           # Match Type (大写B)
        return row

    def _create_campaign_negative_keyword_row(self, keyword_text: str) -> list:
        """创建 Campaign Negative Keyword 行（Campaign Negative Exact）

        注意：Campaign级别的negative keywords不关联ad group，
        因此Ad Group ID (row[4]) 和 Ad Group Name (row[10]) 必须留空
        """
        row = [""] * 31
        row[0] = "Sponsored Products"
        row[1] = "Keyword"
        row[2] = "create"
        row[3] = self.campaign_name
        # row[4] = Ad Group ID - 必须留空！Campaign级别不关联ad group
        row[9] = self.campaign_name
        # row[10] = Ad Group Name - 必须留空！
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
```

---

## 5. API 设计

### 5.1 保存产品信息

#### 端点
```
POST /api/stage4/save-product-info
```

#### 请求体
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "sku": "Flower-BlueFloral2-IP16PM",
  "asin": "B0DRSPRM18",
  "model": "iPhone 16 Pro Max"
}
```

#### 请求验证
- `task_id`: 必须存在于数据库
- `sku`: 字符串，长度 1-100
- `asin`: 字符串，长度 10（亚马逊ASIN固定10位）
- `model`: 枚举值，必须在预设的12个选项中

#### 响应体（成功）
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "product_info": {
    "sku": "Flower-BlueFloral2-IP16PM",
    "asin": "B0DRSPRM18",
    "model": "iPhone 16 Pro Max"
  },
  "saved_at": "2025-11-07T10:30:00Z"
}
```

#### 响应体（失败）
```json
{
  "detail": "任务不存在: 550e8400-e29b-41d4-a716-446655440000"
}
```

#### Pydantic 模型
```python
class PhoneModel(str, Enum):
    """手机型号枚举"""
    IPHONE_16_PRO_MAX = "iPhone 16 Pro Max"
    IPHONE_16_PRO = "iPhone 16 Pro"
    IPHONE_16_PLUS = "iPhone 16 Plus"
    IPHONE_16 = "iPhone 16"
    IPHONE_15_PRO_MAX = "iPhone 15 Pro Max"
    IPHONE_15_PRO = "iPhone 15 Pro"
    IPHONE_15_PLUS = "iPhone 15 Plus"
    IPHONE_15 = "iPhone 15"
    IPHONE_14_PRO_MAX = "iPhone 14 Pro Max"
    IPHONE_14_PRO = "iPhone 14 Pro"
    IPHONE_14_PLUS = "iPhone 14 Plus"
    IPHONE_14 = "iPhone 14"

class ProductInfoRequest(BaseModel):
    task_id: str
    sku: str = Field(..., min_length=1, max_length=100)
    asin: str = Field(..., min_length=10, max_length=10)
    model: PhoneModel

class ProductInfo(BaseModel):
    sku: str
    asin: str
    model: str

class ProductInfoResponse(BaseModel):
    task_id: str
    product_info: ProductInfo
    saved_at: str
```

---

### 5.2 导出 Bulksheet

#### 端点
```
POST /api/stage4/export
```

#### 请求体
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "daily_budget": 3.0,
  "ad_group_default_bid": 0.45,
  "keyword_bid": 0.45,
  "format": "xlsx"
}
```

#### 请求验证
- `task_id`: 必须存在，且已保存产品信息
- `daily_budget`: 浮点数，> 0
- `ad_group_default_bid`: 浮点数，> 0
- `keyword_bid`: 浮点数，> 0
- `format`: 枚举值，目前只支持 "xlsx"

#### 响应（成功）
```
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="bulksheet_Flower-BlueFloral2-IP16PM_blue_iPhone_16_Pro_Max_20251107_143022.xlsx"

[Excel 文件二进制数据]
```

#### 响应（失败）
```json
{
  "detail": "产品信息未保存，请先调用 /api/stage4/save-product-info"
}
```

或

```json
{
  "detail": "没有可导出的搜索词，请先完成 Stage 3"
}
```

#### Pydantic 模型
```python
class ExportFormat(str, Enum):
    """导出格式枚举"""
    XLSX = "xlsx"
    # CSV = "csv"  # 未来扩展

class ExportRequest(BaseModel):
    task_id: str
    daily_budget: float = Field(..., gt=0, description="每日预算（美元）")
    ad_group_default_bid: float = Field(..., gt=0, description="广告组默认出价（美元）")
    keyword_bid: float = Field(..., gt=0, description="关键词出价（美元）")
    format: ExportFormat = ExportFormat.XLSX
```

---

## 6. 数据库设计

### 6.1 Task 表变更

#### 新增字段
```python
class Task(Base):
    __tablename__ = "tasks"

    # ... 原有字段 ...

    # Stage 4 新增字段
    sku = Column(String(100), nullable=True, comment="产品SKU")
    asin = Column(String(10), nullable=True, comment="亚马逊ASIN")
    model = Column(String(50), nullable=True, comment="手机型号")
```

#### 数据迁移
```python
# 不需要迁移脚本，字段都是 nullable=True
# 旧任务的这些字段为 NULL，不影响 Stage 1-3 功能
```

### 6.2 CRUD 操作

#### crud/task.py 新增方法

```python
def update_product_info(
    db: Session,
    task_id: str,
    sku: str,
    asin: str,
    model: str
) -> Task:
    """
    更新任务的产品信息

    Args:
        db: 数据库会话
        task_id: 任务ID
        sku: 产品SKU
        asin: 亚马逊ASIN
        model: 手机型号

    Returns:
        更新后的 Task 对象

    Raises:
        ValueError: 任务不存在
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise ValueError(f"任务不存在: {task_id}")

    task.sku = sku
    task.asin = asin
    task.model = model
    db.commit()
    db.refresh(task)

    return task


def get_product_info(db: Session, task_id: str) -> dict:
    """
    获取任务的产品信息

    Returns:
        {sku, asin, model} 或 None（未保存）
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise ValueError(f"任务不存在: {task_id}")

    if not task.sku or not task.asin or not task.model:
        return None

    return {
        "sku": task.sku,
        "asin": task.asin,
        "model": task.model
    }
```

#### crud/search_term.py 新增方法

```python
def get_valid_search_terms(db: Session, task_id: str) -> List[SearchTerm]:
    """
    获取所有有效的搜索词（用于导出）

    Args:
        db: 数据库会话
        task_id: 任务ID

    Returns:
        有效搜索词列表
    """
    return db.query(SearchTerm).filter(
        SearchTerm.task_id == task_id,
        SearchTerm.is_valid == True,
        SearchTerm.is_deleted == False
    ).all()
```

#### crud/entity_word.py 新增方法

```python
def get_all_entity_words(db: Session, task_id: str) -> List[EntityWord]:
    """
    获取所有本体词变体（用于 Negative Keyword）

    Args:
        db: 数据库会话
        task_id: 任务ID

    Returns:
        本体词列表
    """
    return db.query(EntityWord).filter(
        EntityWord.task_id == task_id,
        EntityWord.is_deleted == False
    ).all()
```

---

## 7. 实施计划

### 7.1 开发任务

#### 任务1：数据库变更（30分钟）
- [ ] 修改 `models_db.py`：Task 表新增3个字段
- [ ] 测试数据库变更（创建新任务，验证字段）

#### 任务2：Pydantic 模型（30分钟）
- [ ] 在 `models.py` 添加：
  - `PhoneModel` 枚举
  - `ProductInfoRequest`
  - `ProductInfoResponse`
  - `ExportRequest`
  - `ExportFormat` 枚举

#### 任务3：CRUD 操作（1小时）
- [ ] `crud/task.py`：
  - `update_product_info()`
  - `get_product_info()`
- [ ] `crud/search_term.py`：
  - `get_valid_search_terms()`
- [ ] `crud/entity_word.py`：
  - `get_all_entity_words()`

#### 任务4：Bulksheet 生成服务（2小时）
- [ ] 创建 `services/bulksheet_generator.py`
- [ ] 实现 `BulksheetGenerator` 类
- [ ] 实现31列完整结构
- [ ] 实现4种 Entity 行生成（Campaign, Ad Group, Product Ad, Keyword）
- [ ] 实现 Campaign Negative Keyword 行生成

#### 任务5：API 端点（1小时）
- [ ] `main.py` 添加：
  - `POST /api/stage4/save-product-info`
  - `POST /api/stage4/export`
- [ ] 错误处理和验证

#### 任务6：测试（1.5小时）
- [ ] 单元测试：BulksheetGenerator 类
- [ ] 集成测试：完整导出流程
- [ ] 验证导出文件与模版一致
- [ ] Replit 部署测试

### 7.2 开发顺序

```
Day 1:
1. 数据库变更 + Pydantic 模型（1小时）
2. CRUD 操作（1小时）
3. 测试 API 1: save-product-info（30分钟）

Day 2:
4. Bulksheet 生成服务（2小时）
5. 测试生成逻辑（30分钟）

Day 3:
6. API 2: export（1小时）
7. 集成测试（1小时）
8. Replit 部署（30分钟）
```

### 7.3 测试用例

#### 测试1：保存产品信息
```bash
curl -X POST http://localhost:8000/api/stage4/save-product-info \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "xxx",
    "sku": "Flower-BlueFloral2-IP16PM",
    "asin": "B0DRSPRM18",
    "model": "iPhone 16 Pro Max"
  }'
```

#### 测试2：导出 Bulksheet
```bash
curl -X POST http://localhost:8000/api/stage4/export \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "xxx",
    "daily_budget": 3.0,
    "ad_group_default_bid": 0.45,
    "keyword_bid": 0.45,
    "format": "xlsx"
  }' \
  --output bulksheet.xlsx
```

#### 测试3：验证文件结构
```python
import openpyxl

wb = openpyxl.load_workbook('bulksheet.xlsx')
sheet = wb.active

assert sheet.max_column == 31  # 31列
assert sheet.cell(2, 2).value == "Campaign"  # Row 2 是 Campaign
assert sheet.cell(3, 2).value == "Ad Group"   # Row 3 是 Ad Group
assert sheet.cell(4, 2).value == "Product Ad" # Row 4 是 Product Ad
assert sheet.cell(5, 2).value == "Keyword"    # Row 5 开始是 Keyword
```

---

## 8. 注意事项

### 8.1 数据一致性
- 导出前必须验证：
  - 产品信息已保存
  - 存在有效搜索词（is_valid=True）
  - Task 状态为 "combined"

### 8.2 性能考虑
- 大量关键词（>1000）：使用批量写入
- 内存控制：使用 BytesIO 而非临时文件
- 响应超时：设置合理的超时时间（建议60秒）

### 8.3 错误处理
- 产品信息未保存 → 返回 400 错误
- 无有效搜索词 → 返回 400 错误
- Excel 生成失败 → 返回 500 错误，记录详细日志

### 8.4 未来扩展
- [ ] 支持 CSV 格式导出
- [ ] 支持自定义 Match Type（用户可选）
- [ ] 支持批量导出多个任务
- [ ] 支持导出历史记录

---

## 9. 附录

### 9.1 亚马逊 Bulksheet 官方文档
- [Amazon Advertising API Documentation](https://advertising.amazon.com/API/docs)
- [Bulksheet Upload Guidelines](https://advertising.amazon.com/help#GHTRFDZRJPW6764R)

### 9.2 相关文件
- 模版文件：`/Users/linshaoyong/Desktop/词根分析2/Flower-BlueFloral2/...`
- Stage 3 文档：`backend_v2/docs/stage3_development_summary.md`
- 项目需求文档：`项目需求文档.md`

---

**文档结束**

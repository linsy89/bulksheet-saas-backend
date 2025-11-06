# Stage 3 需求文档 - 本体词扩展与搜索词组合

**项目**: Bulksheet SaaS
**版本**: v1.0
**文档日期**: 2025-11-06
**状态**: 需求确认完成，待开发
**目标读者**: 产品经理、后端工程师、前端工程师

---

## 目录

- [1. 项目概述](#1-项目概述)
- [2. 功能概述](#2-功能概述)
- [3. 用户工作流](#3-用户工作流)
- [4. 数据库设计](#4-数据库设计)
- [5. API 设计](#5-api-设计)
- [6. 业务规则](#6-业务规则)
- [7. AI Prompt 设计](#7-ai-prompt-设计)
- [8. 技术架构](#8-技术架构)
- [9. 测试用例](#9-测试用例)
- [10. 实施计划](#10-实施计划)

---

## 1. 项目概述

### 1.1 背景

在完成 Stage 1（属性词生成）和 Stage 2（属性词筛选）后，用户已经拥有了精选的属性词列表。Stage 3 的目标是将这些属性词与本体词组合，生成完整的搜索关键词。

### 1.2 核心概念

**本体词（Product Entity Term）**
- 定义：描述"商品是什么"的核心词汇
- 示例：`iphone 14 case`、`laptop stand`、`wireless earbuds`
- 作用：确定商品类别和产品范围

**本体词扩展的必要性**
用户在搜索商品时，可能使用不同的表达方式：
- 同义词：`case` → `cover`、`shell`、`protector`
- 变体：`iphone 14 case` → `iphone14 case`（去空格）、`case for iphone 14`（介词组合）

通过扩展本体词，可以覆盖更多用户搜索习惯，提升广告覆盖率。

### 1.3 Stage 3 的价值

- **全面覆盖**：通过笛卡尔积组合，生成所有可能的搜索词
- **智能扩展**：AI 自动生成本体词同义词和变体
- **用户可控**：支持筛选、编辑、删除本体词和搜索词
- **数据持久化**：所有数据保存到数据库，支持任务恢复

### 1.4 整体流程

```
Stage 1: 生成属性词
    ↓
Stage 2: 筛选属性词 → 得到 N 个已选属性词
    ↓
Stage 3.1: 扩展本体词 → AI 生成本体词变体
    ↓
Stage 3.2: 筛选本体词 → 得到 M 个已选本体词
    ↓
Stage 3.3: 组合搜索词 → 生成 N × M 个搜索词
    ↓
Stage 3.4: 查看搜索词列表
    ↓
Stage 4: 导出 Bulksheet
```

---

## 2. 功能概述

### 2.1 功能模块

Stage 3 包含 **4 个核心功能模块**：

| 模块 | 功能描述 | 用户价值 |
|------|---------|---------|
| **3.1 本体词扩展** | AI 生成本体词的同义词和变体 | 自动化，节省人工时间 |
| **3.2 本体词筛选** | 查看、勾选、添加、删除本体词 | 用户可控，提升质量 |
| **3.3 搜索词组合** | 属性词 × 本体词生成完整搜索词 | 一键生成，效率高 |
| **3.4 搜索词管理** | 查看、筛选、删除搜索词 | 灵活管理，按需调整 |

### 2.2 功能边界

**包含的功能**：
- ✅ 本体词 AI 扩展（同义词 + 变体）
- ✅ 本体词列表管理（查看、筛选、添加、删除）
- ✅ 搜索词笛卡尔积组合
- ✅ 搜索词列表查看（支持分页、筛选）
- ✅ 搜索词批量删除
- ✅ 任务状态管理

**不包含的功能**（后续迭代）：
- ❌ 多属性词组合（如 `cute + red + phone case`）
- ❌ 搜索词统计分析
- ❌ 本体词生成预览（直接生成并保存）
- ❌ 搜索词效果评估（需要广告数据）

---

## 3. 用户工作流

### 3.1 完整流程图

```
┌──────────────────────────────────────────────────────────┐
│ 前提条件：用户已完成 Stage 2，拥有 N 个已选属性词         │
│ 任务状态：status = "selected"                              │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 1: 生成本体词变体                                     │
│ - 点击"生成本体词变体"按钮                                 │
│ - 系统调用 AI，自动生成同义词和变体                        │
│ - 显示加载状态（预计 5-10 秒）                             │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 2: 查看本体词列表                                     │
│ - 显示 AI 生成的 8-15 个本体词                             │
│ - 每个本体词显示：                                         │
│   * 本体词文本                                             │
│   * 类型（原词/同义词/变体）                               │
│   * 中文说明                                               │
│   * 适用场景                                               │
│   * 推荐度（✅/⚠️）                                        │
│   * 搜索价值（⭐星级）                                    │
│   * 复选框（选中状态）                                     │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 3: 编辑本体词列表                                     │
│ - 勾选/取消勾选本体词                                      │
│ - 点击"添加自定义本体词"按钮                               │
│   * 弹出输入框，输入本体词文本                             │
│   * 保存后自动添加到列表（默认选中）                       │
│ - 删除不需要的本体词（点击删除图标）                       │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 4: 保存本体词选择                                     │
│ - 点击"保存选择"按钮                                       │
│ - 系统保存选中状态                                         │
│ - 显示保存成功提示：                                       │
│   "已选择 6 个本体词（共 10 个）"                          │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 5: 生成搜索词组合                                     │
│ - 点击"生成搜索词"按钮                                     │
│ - 系统计算：15 个属性词 × 6 个本体词 = 90 个搜索词         │
│ - 显示生成进度                                             │
│ - 生成完成后跳转到搜索词列表页                             │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 6: 查看搜索词列表                                     │
│ - 显示所有生成的搜索词（分页显示）                         │
│ - 支持筛选：                                               │
│   * 按属性词筛选                                           │
│   * 按本体词筛选                                           │
│ - 每个搜索词显示：                                         │
│   * 完整搜索词文本                                         │
│   * 组成部分（属性词 + 本体词）                            │
│   * 字符长度                                               │
│   * 删除按钮                                               │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 7: （可选）批量删除搜索词                             │
│ - 勾选多个搜索词                                           │
│ - 点击"批量删除"按钮                                       │
│ - 确认后删除选中的搜索词                                   │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│ Step 8: 进入 Stage 4（导出 Bulksheet）                    │
└──────────────────────────────────────────────────────────┘
```

### 3.2 关键页面交互

#### 页面 1：本体词列表页

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│ Stage 3: 本体词扩展与筛选                                │
├─────────────────────────────────────────────────────────┤
│ 原始本体词: iphone 14 case                               │
│ [生成本体词变体] 按钮（如果未生成）                      │
├─────────────────────────────────────────────────────────┤
│ 已选择: 6/10 个本体词                                     │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ☑ iphone 14 case (原词) ✅ ⭐⭐⭐⭐⭐              │ │
│ │   iPhone 14 手机壳（原始输入）                       │ │
│ │   适用场景: 用户标准搜索词                           │ │
│ │   [删除]                                             │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ☑ iphone 14 cover (同义词) ✅ ⭐⭐⭐⭐⭐           │ │
│ │   保护套（同义词，使用频率高）                       │ │
│ │   适用场景: 用户常用的替代表达                       │ │
│ │   [删除]                                             │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ ☐ iphone14 case (变体) ⚠️ ⭐⭐⭐                  │ │
│ │   去空格变体                                         │ │
│ │   适用场景: 用户快速输入时可能省略空格               │ │
│ │   [删除]                                             │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ [+ 添加自定义本体词]                                     │
│                                                          │
│ [保存选择] [生成搜索词]                                  │
└─────────────────────────────────────────────────────────┘
```

#### 页面 2：搜索词列表页

**布局**：
```
┌─────────────────────────────────────────────────────────┐
│ Stage 3: 搜索词列表                                      │
├─────────────────────────────────────────────────────────┤
│ 共生成 90 个搜索词                                        │
│                                                          │
│ 筛选: [属性词 ▼] [本体词 ▼]                              │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ cute iphone 14 case                                  │ │
│ │ 属性词: cute | 本体词: iphone 14 case | 长度: 22    │ │
│ │ [删除]                                               │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ cute iphone 14 cover                                 │ │
│ │ 属性词: cute | 本体词: iphone 14 cover | 长度: 23   │ │
│ │ [删除]                                               │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                          │
│ ... (显示更多搜索词)                                      │
│                                                          │
│ [批量删除] [导出到 Stage 4]                              │
│ [上一页] 第 1/9 页 [下一页]                              │
└─────────────────────────────────────────────────────────┘
```

---

## 4. 数据库设计

### 4.1 新增表 1: entity_words（本体词表）

**表名**: `entity_words`

**功能**: 存储任务的本体词扩展结果

**字段设计**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY AUTO_INCREMENT | - | 主键ID |
| task_id | VARCHAR(36) | NOT NULL, INDEX | - | 关联任务ID（外键） |
| concept | VARCHAR(200) | NOT NULL | - | 原始属性概念（关联tasks.concept）✨ |
| entity_word | VARCHAR(200) | NOT NULL | - | 本体词文本 |
| type | VARCHAR(50) | NOT NULL | - | 类型: original/synonym/variant |
| translation | TEXT | - | NULL | 中文说明 |
| use_case | TEXT | - | NULL | 适用场景描述 |
| recommended | BOOLEAN | NOT NULL | true | 是否推荐使用 |
| search_value | VARCHAR(20) | NOT NULL | 'medium' | 搜索价值: high/medium/low |
| search_value_stars | INTEGER | NOT NULL | 3 | 搜索价值星级(1-5) |
| source | VARCHAR(20) | NOT NULL | 'ai' | 来源: ai/user |
| is_selected | BOOLEAN | NOT NULL | true | 是否选中参与组合 |
| is_deleted | BOOLEAN | NOT NULL | false | 是否软删除 |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引设计**:
```sql
-- 主键索引（自动创建）
PRIMARY KEY (id)

-- 外键索引
INDEX idx_entity_task_id (task_id)

-- 查询优化索引
INDEX idx_entity_task_deleted (task_id, is_deleted)
INDEX idx_entity_task_selected (task_id, is_selected, is_deleted)
```

**外键约束**:
```sql
FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
```

**类型枚举说明**:
- `original` - 原始本体词（用户输入）
- `synonym` - 同义词（如 `case` → `cover`）
- `variant` - 变体（包含空格变化、简写、介词组合、单复数、连字符等）

**来源枚举说明**:
- `ai` - AI 生成
- `user` - 用户手动添加

---

### 4.2 新增表 2: search_terms（搜索词表）

**表名**: `search_terms`

**功能**: 存储属性词和本体词组合生成的完整搜索词

**字段设计**:

| 字段名 | 数据类型 | 约束 | 默认值 | 说明 |
|--------|---------|------|--------|------|
| id | INTEGER | PRIMARY KEY AUTO_INCREMENT | - | 主键ID |
| task_id | VARCHAR(36) | NOT NULL, INDEX | - | 关联任务ID（外键） |
| term | VARCHAR(300) | NOT NULL | - | 完整搜索词 |
| attribute_word_id | INTEGER | NOT NULL | - | 属性词ID（外键） |
| attribute_word | VARCHAR(100) | NOT NULL | - | 属性词文本（冗余） |
| entity_word_id | INTEGER | NOT NULL | - | 本体词ID（外键） |
| entity_word | VARCHAR(200) | NOT NULL | - | 本体词文本（冗余） |
| length | INTEGER | NOT NULL | - | 搜索词字符长度 |
| is_valid | BOOLEAN | NOT NULL | true | 是否有效（长度验证） |
| is_deleted | BOOLEAN | NOT NULL | false | 是否软删除 |
| created_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | CURRENT_TIMESTAMP | 更新时间 |

**索引设计**:
```sql
-- 主键索引（自动创建）
PRIMARY KEY (id)

-- 外键索引
INDEX idx_search_task_id (task_id)
INDEX idx_search_attr_id (attribute_word_id)
INDEX idx_search_entity_id (entity_word_id)

-- 查询优化索引
INDEX idx_search_task_deleted (task_id, is_deleted)
INDEX idx_search_term_unique (task_id, term, is_deleted)
```

**外键约束**:
```sql
FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE
FOREIGN KEY (attribute_word_id) REFERENCES task_attributes(id) ON DELETE CASCADE
FOREIGN KEY (entity_word_id) REFERENCES entity_words(id) ON DELETE CASCADE
```

**设计说明**:
- **冗余存储**：`attribute_word` 和 `entity_word` 字段冗余存储文本，避免查询时频繁 JOIN
- **唯一性处理**：通过索引 `idx_search_term_unique` 保证同一任务中不会有重复的搜索词。重新生成前，物理删除（DELETE）已软删除的记录，避免冲突 ✨
- **级联删除**：删除任务时自动删除所有关联的搜索词
- **软删除级联**：删除本体词或属性词时，自动级联软删除相关的搜索词 ✨

---

### 4.3 修改表: tasks（任务表）

**修改内容**: 扩展 `status` 字段的枚举值

**新增状态值**:
```sql
ALTER TABLE tasks MODIFY COLUMN status VARCHAR(50) NOT NULL DEFAULT 'draft';

-- 状态枚举（代码层面控制）
-- 'draft'             - 草稿（Stage 1 生成后）
-- 'selected'          - 已选择属性词（Stage 2 保存后）
-- 'entity_expanded'   - 本体词已扩展（Stage 3.1 完成）✨ 新增
-- 'entity_selected'   - 本体词已筛选（Stage 3.2 完成）✨ 新增
-- 'combined'          - 搜索词已组合（Stage 3.3 完成）✨ 新增
-- 'exported'          - 已导出（Stage 4 完成）
```

**状态流转图**:
```
draft → selected → entity_expanded → entity_selected → combined → exported
 ↑                                                                      ↓
 └──────────────────────────── (用户可重新编辑) ──────────────────────┘
```

---

### 4.4 数据库关系图（ER 图）

```
┌─────────────────┐
│     tasks       │
│─────────────────│
│ task_id (PK)    │──┐
│ concept         │  │
│ entity_word     │  │
│ status          │  │
│ created_at      │  │
│ updated_at      │  │
└─────────────────┘  │
                     │
        ┌────────────┼────────────┐
        │            │            │
        │            │            │
        ↓            ↓            ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│task_attributes│ │entity_words  │ │search_terms  │
│──────────────│ │──────────────│ │──────────────│
│ id (PK)      │ │ id (PK)      │ │ id (PK)      │
│ task_id (FK) │ │ task_id (FK) │ │ task_id (FK) │
│ word         │ │ entity_word  │ │ term         │
│ is_selected  │ │ type         │ │ attr_word_id │─┐
│ ...          │ │ is_selected  │ │ entity_id    │─┼─┐
└──────────────┘ │ ...          │ │ length       │ │ │
      ↑          └──────────────┘ │ ...          │ │ │
      │                 ↑          └──────────────┘ │ │
      │                 │                 ↓         │ │
      └─────────────────┼─────────────────┘         │ │
                        └───────────────────────────┘ │
                                                      │
                        (外键关联) ───────────────────┘
```

**关系说明**:
1. `tasks` (1) ↔ (N) `task_attributes` - 一个任务有多个属性词
2. `tasks` (1) ↔ (N) `entity_words` - 一个任务有多个本体词
3. `tasks` (1) ↔ (N) `search_terms` - 一个任务有多个搜索词
4. `task_attributes` (1) ↔ (N) `search_terms` - 一个属性词可组合生成多个搜索词
5. `entity_words` (1) ↔ (N) `search_terms` - 一个本体词可组合生成多个搜索词

---

## 5. API 设计

### 5.1 API 概览

| 序号 | 方法 | 端点 | 功能 | 状态码 |
|------|------|------|------|--------|
| 1 | POST | `/api/stage3/tasks/{task_id}/entity-words/generate` | 生成本体词变体 | 200/400/404/500 |
| 2 | GET | `/api/stage3/tasks/{task_id}/entity-words` | 查询本体词列表 | 200/404 |
| 3 | PUT | `/api/stage3/tasks/{task_id}/entity-words/selection` | 更新本体词选择 | 200/400/404 |
| 4 | POST | `/api/stage3/tasks/{task_id}/search-terms` | 生成搜索词组合 | 200/400/404/500 |
| 5 | GET | `/api/stage3/tasks/{task_id}/search-terms` | 查询搜索词列表 | 200/404 |
| 6 | DELETE | `/api/stage3/tasks/{task_id}/search-terms/batch` | 批量删除搜索词 | 200/400/404 |

---

### 5.2 API 详细设计

#### API 1: 生成本体词变体

**端点**: `POST /api/stage3/tasks/{task_id}/entity-words/generate`

**功能**: 调用 AI 为本体词生成同义词和变体

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID（UUID格式） |

**请求体** (可选):
```json
{
  "options": {
    "max_count": 15,
    "include_variants": true
  }
}
```

**请求字段说明**:
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| options | object | 否 | - | 生成选项 |
| options.max_count | integer | 否 | 15 | 最大生成数量 |
| options.include_variants | boolean | 否 | true | 是否包含变体 |

**处理逻辑**:
1. **验证任务状态** ✨：检查状态是否允许生成本体词（`selected`, `entity_expanded`, `entity_selected`, `combined`）
2. 验证 `task_id` 是否存在
3. 从 `tasks` 表读取 `entity_word`（如 `iphone 14 case`）
4. **验证本体词格式** ✨：只允许英文、数字、空格、连字符，长度 ≤ 200
5. 检查是否已生成（`entity_words` 表是否有记录）
6. 如果已生成，返回错误提示（避免重复生成）
7. **调用 AI 服务（带重试）** ✨：最多重试 3 次，间隔 2 秒
8. 解析 AI 响应，转换为标准格式
9. 批量保存到 `entity_words` 表（所有词默认 `is_selected=true`，包含 `concept` 字段）
10. 更新任务状态为 `entity_expanded`
11. 返回生成结果

**响应体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "original_entity_word": "iphone 14 case",
  "entity_words": [
    {
      "id": 1,
      "entity_word": "iphone 14 case",
      "type": "original",
      "translation": "iPhone 14 手机壳（原始输入）",
      "use_case": "用户标准搜索词",
      "recommended": true,
      "search_value": "high",
      "search_value_stars": 5,
      "source": "ai",
      "is_selected": true
    },
    {
      "id": 2,
      "entity_word": "iphone 14 cover",
      "type": "synonym",
      "translation": "保护套（同义词，使用频率高）",
      "use_case": "用户常用的替代表达",
      "recommended": true,
      "search_value": "high",
      "search_value_stars": 5,
      "source": "ai",
      "is_selected": true
    },
    {
      "id": 3,
      "entity_word": "iphone 14 phone case",
      "type": "variant",
      "translation": "添加 'phone' 的完整表达",
      "use_case": "更明确的产品描述",
      "recommended": true,
      "search_value": "high",
      "search_value_stars": 4,
      "source": "ai",
      "is_selected": true
    },
    {
      "id": 4,
      "entity_word": "case for iphone 14",
      "type": "variant",
      "translation": "介词组合（自然语言顺序）",
      "use_case": "用户使用自然语言搜索",
      "recommended": true,
      "search_value": "high",
      "search_value_stars": 4,
      "source": "ai",
      "is_selected": true
    },
    {
      "id": 5,
      "entity_word": "iphone14 case",
      "type": "variant",
      "translation": "去空格变体",
      "use_case": "用户快速输入时可能省略空格",
      "recommended": false,
      "search_value": "medium",
      "search_value_stars": 3,
      "source": "ai",
      "is_selected": true
    }
  ],
  "metadata": {
    "total_count": 10,
    "original_count": 1,
    "synonym_count": 3,
    "variant_count": 6,
    "generated_at": "2025-11-06T10:00:00Z"
  }
}
```

**状态码**:
- `200 OK` - 成功生成
- `400 Bad Request` - 参数错误或已生成过本体词
- `404 Not Found` - 任务不存在
- `500 Internal Server Error` - AI 服务调用失败

**错误响应示例**:
```json
{
  "detail": "本体词已生成，请直接查看或重新生成",
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "existing_count": 10
}
```

---

#### API 2: 查询本体词列表

**端点**: `GET /api/stage3/tasks/{task_id}/entity-words`

**功能**: 获取任务的所有本体词（不含已删除）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID（UUID格式） |

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| include_deleted | boolean | 否 | false | 是否包含已删除的本体词 |

**处理逻辑**:
1. 验证 `task_id` 是否存在
2. 查询 `entity_words` 表（`task_id` = 指定值，`is_deleted` = false）
3. 按 `search_value_stars` 降序、`id` 升序排序
4. 计算元数据统计

**响应体**: 同 API 1

**状态码**:
- `200 OK` - 成功
- `404 Not Found` - 任务不存在或未生成本体词

---

#### API 3: 更新本体词选择

**端点**: `PUT /api/stage3/tasks/{task_id}/entity-words/selection`

**功能**: 保存用户的本体词选择（勾选、添加、删除）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID（UUID格式） |

**请求体**:
```json
{
  "selected_entity_word_ids": [1, 2, 4, 5],
  "new_entity_words": [
    {
      "entity_word": "case for iphone 14 pro"
    },
    {
      "entity_word": "iphone 14 protective case"
    }
  ],
  "deleted_entity_word_ids": [8, 10]
}
```

**请求字段说明**:
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| selected_entity_word_ids | array | 否 | [] | 选中的本体词ID列表 |
| new_entity_words | array | 否 | [] | 新增的自定义本体词 |
| new_entity_words[].entity_word | string | 是 | - | 本体词文本 |
| deleted_entity_word_ids | array | 否 | [] | 要删除的本体词ID列表 |

**处理逻辑**:
1. 验证 `task_id` 是否存在
2. 验证所有 ID 是否属于该任务
3. **验证空选择** ✨：如果 `selected_count == 0 && new_entity_words.length == 0`，返回错误（至少需要选择 1 个本体词）
4. **更新选中状态**：
   - 将该任务所有本体词设置为 `is_selected=false`
   - 将 `selected_entity_word_ids` 中的ID设置为 `is_selected=true`
5. **添加自定义本体词**：
   - 遍历 `new_entity_words`
   - 创建新记录（`type='original'`, `source='user'`, `is_selected=true`，`concept` 从 tasks 表读取）
6. **软删除本体词（级联）** ✨：
   - 将 `deleted_entity_word_ids` 中的ID设置为 `is_deleted=true`, `is_selected=false`
   - 级联软删除相关的搜索词（`search_terms.entity_word_id IN deleted_ids`）
7. 更新任务状态为 `entity_selected`
8. 查询并返回最新统计

**响应体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "entity_selected",
  "updated_at": "2025-11-06T10:15:00Z",
  "metadata": {
    "selected_count": 6,
    "total_count": 11,
    "changes": {
      "selected": 4,
      "added": 2,
      "deleted": 2
    }
  }
}
```

**状态码**:
- `200 OK` - 成功
- `400 Bad Request` - 参数错误或ID不属于该任务
- `404 Not Found` - 任务不存在

---

#### API 4: 生成搜索词组合

**端点**: `POST /api/stage3/tasks/{task_id}/search-terms`

**功能**: 组合属性词和本体词，生成完整搜索词

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID（UUID格式） |

**请求体** (可选):
```json
{
  "options": {
    "max_length": 80,
    "deduplicate": true
  }
}
```

**请求字段说明**:
| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| options | object | 否 | - | 组合选项 |
| options.max_length | integer | 否 | 80 | 最大字符长度 |
| options.deduplicate | boolean | 否 | true | 是否去重 |

**处理逻辑**:
1. **验证任务状态** ✨：检查状态是否允许生成搜索词（`entity_selected`, `combined`）
2. 验证 `task_id` 是否存在
3. 查询已选中的属性词（`task_attributes.is_selected=true`）
4. 查询已选中的本体词（`entity_words.is_selected=true`）
5. 如果属性词或本体词为空，返回错误
6. **验证笛卡尔积上限** ✨：如果 `attr_count × entity_count > 1000`，返回错误（超过上限，请减少选择）
7. **幂等操作** ✨：
   - 物理删除已软删除的记录：`DELETE FROM search_terms WHERE task_id = ? AND is_deleted = true`
   - 软删除现有有效记录：`UPDATE search_terms SET is_deleted = true WHERE task_id = ? AND is_deleted = false`
8. 笛卡尔积组合：
   ```python
   for attribute in selected_attributes:
       for entity in selected_entity_words:
           term = f"{attribute.word} {entity.entity_word}"
           length = len(term)
           is_valid = length <= max_length
           # 保存到 search_terms 表
   ```
9. 如果启用去重，检查是否已存在相同的 `term`
10. 批量插入 `search_terms` 表
11. 更新任务状态为 `combined`
12. 返回生成结果

**响应体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "search_terms": [
    {
      "id": 1,
      "term": "cute iphone 14 case",
      "attribute_word": "cute",
      "entity_word": "iphone 14 case",
      "length": 22,
      "is_valid": true
    },
    {
      "id": 2,
      "term": "cute iphone 14 cover",
      "attribute_word": "cute",
      "entity_word": "iphone 14 cover",
      "length": 23,
      "is_valid": true
    },
    {
      "id": 3,
      "term": "adorable iphone 14 case",
      "attribute_word": "adorable",
      "entity_word": "iphone 14 case",
      "length": 26,
      "is_valid": true
    }
  ],
  "metadata": {
    "total_terms": 90,
    "valid_terms": 90,
    "invalid_terms": 0,
    "attribute_count": 15,
    "entity_word_count": 6,
    "average_length": 24.5,
    "min_length": 18,
    "max_length": 32,
    "generated_at": "2025-11-06T10:20:00Z"
  }
}
```

**状态码**:
- `200 OK` - 成功生成
- `400 Bad Request` - 没有选中的属性词或本体词
- `404 Not Found` - 任务不存在
- `500 Internal Server Error` - 数据库保存失败

---

#### API 5: 查询搜索词列表

**端点**: `GET /api/stage3/tasks/{task_id}/search-terms`

**功能**: 获取任务的所有搜索词（支持分页和筛选）

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID（UUID格式） |

**查询参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码（从1开始） |
| page_size | integer | 否 | 20 | 每页数量 |
| filter_by_attribute | string | 否 | - | 按属性词筛选（精确匹配） |
| filter_by_entity | string | 否 | - | 按本体词筛选（精确匹配） |
| include_deleted | boolean | 否 | false | 是否包含已删除的搜索词 |

**处理逻辑**:
1. 验证 `task_id` 是否存在
2. 构建查询条件：
   - `task_id` = 指定值
   - `is_deleted` = false（除非 `include_deleted=true`）
   - 如果指定 `filter_by_attribute`，添加过滤条件
   - 如果指定 `filter_by_entity`，添加过滤条件
3. 计算总数和分页
4. 按 `id` 升序排序
5. 返回分页数据

**响应体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "search_terms": [
    {
      "id": 1,
      "term": "cute iphone 14 case",
      "attribute_word": "cute",
      "entity_word": "iphone 14 case",
      "length": 22,
      "is_valid": true
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "total_count": 90
  },
  "metadata": {
    "total_terms": 90,
    "valid_terms": 90,
    "invalid_terms": 0,
    "average_length": 24.5
  }
}
```

**状态码**:
- `200 OK` - 成功
- `404 Not Found` - 任务不存在或未生成搜索词

---

#### API 6: 批量删除搜索词

**端点**: `DELETE /api/stage3/tasks/{task_id}/search-terms/batch`

**功能**: 批量软删除搜索词

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| task_id | string | 是 | 任务ID（UUID格式） |

**请求体**:
```json
{
  "search_term_ids": [5, 12, 18, 25]
}
```

**请求字段说明**:
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| search_term_ids | array | 是 | 要删除的搜索词ID列表 |

**处理逻辑**:
1. 验证 `task_id` 是否存在
2. **验证所有 ID 存在且属于该任务** ✨：先查询验证所有 ID，如果有不存在的或不属于该任务的 ID，返回错误（原子操作）
3. **批量软删除（事务）** ✨：在单个事务中将所有指定 ID 的记录设置为 `is_deleted=true`
4. 返回删除统计

**响应体**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "deleted_count": 4,
  "remaining_count": 86,
  "message": "已成功删除 4 个搜索词"
}
```

**状态码**:
- `200 OK` - 成功
- `400 Bad Request` - ID列表为空或ID不属于该任务
- `404 Not Found` - 任务不存在

---

## 6. 业务规则

### 6.1 本体词生成规则

#### 6.1.1 生成数量
- 默认生成 **8-15 个**本体词（包含原词）
- 至少包含 **2 个同义词**（如果存在）
- 至少包含 **3 个变体**

#### 6.1.2 类型分布
- **1 个原词**（用户输入）
- **2-4 个同义词**（常用的替代表达）
- **5-10 个变体**（各种形式变化）

#### 6.1.3 变体类型

**1. 空格变化**
- `iphone 14 case` → `iphone14 case`
- `laptop stand` → `laptopstand`

**2. 简写/省略**
- `iphone 14 case` → `14 case`
- `wireless earbuds` → `earbuds`

**3. 介词组合**
- `iphone 14 case` → `case for iphone 14`
- `laptop stand` → `stand for laptop`

**4. 单复数**
- `case` → `cases`
- `stand` → `stands`

**5. 连字符变化**
- `phone case` → `phone-case`
- `laptop stand` → `laptop-stand`

#### 6.1.4 质量标准
- **保持产品类型不变**：不能改变产品类别
  - ❌ 错误：`iphone 14 case` → `iphone 14 screen protector`
  - ✅ 正确：`iphone 14 case` → `iphone 14 cover`
- **覆盖用户习惯**：考虑常见搜索模式
- **美式英语优先**：当前版本只生成美式英语

---

### 6.2 本体词筛选规则

#### 6.2.1 默认选中状态
- AI 生成的本体词**默认全部选中**（`is_selected=true`）
- 用户可以取消勾选不需要的本体词

#### 6.2.2 自定义本体词
- 用户添加的本体词**默认选中**
- `source` 字段标记为 `user`
- `type` 字段标记为 `original`

#### 6.2.3 软删除机制
- 删除操作只是将 `is_deleted` 设置为 `true`
- 不会物理删除数据库记录
- 查询时默认过滤已删除的记录

---

### 6.3 搜索词组合规则

#### 6.3.1 组合公式
```
搜索词 = 属性词 + 空格 + 本体词
```

**示例**:
- 属性词: `cute`
- 本体词: `iphone 14 case`
- 搜索词: `cute iphone 14 case`

#### 6.3.2 组合策略
- **笛卡尔积**：每个已选属性词 × 每个已选本体词
- **示例计算**：
  - 15 个属性词 × 6 个本体词 = **90 个搜索词**

#### 6.3.3 验证规则

**1. 长度验证**
- 默认最大长度：**80 字符**
- 超过长度的搜索词标记为 `is_valid=false`

**2. 去重规则**
- 同一任务中，相同的 `term` 只保存一次
- 通过索引 `idx_search_term_unique` 保证唯一性

**3. 特殊字符处理**
- 暂不过滤特殊字符（保留原样）
- 未来可扩展：过滤表情符号、HTML标签等

---

### 6.4 任务状态流转规则

| 当前状态 | 操作 | 目标状态 |
|---------|------|---------|
| `selected` | 生成本体词 | `entity_expanded` |
| `entity_expanded` | 保存本体词选择 | `entity_selected` |
| `entity_selected` | 生成搜索词组合 | `combined` |
| `combined` | 重新编辑本体词 | `entity_selected` |
| `combined` | 重新编辑属性词 | `selected` |

**状态回退规则**：
- 用户可以随时返回上一步重新编辑
- 回退后，状态相应降级

---

### 6.5 状态前置条件验证规则 ✨

#### 6.5.1 API 1（生成本体词）状态验证
- **允许的状态**：`selected`, `entity_expanded`, `entity_selected`, `combined`
- **拒绝的状态**：`draft`, `exported`
- **错误提示**：`当前任务状态不允许生成本体词，请先完成属性词筛选`

#### 6.5.2 API 4（生成搜索词）状态验证
- **允许的状态**：`entity_selected`, `combined`
- **拒绝的状态**：`draft`, `selected`, `entity_expanded`, `exported`
- **错误提示**：`当前任务状态不允许生成搜索词，请先完成本体词筛选`

---

### 6.6 级联软删除规则 ✨

#### 6.6.1 删除本体词时的级联
- **触发条件**：API 3 中 `deleted_entity_word_ids` 不为空
- **级联操作**：
  1. 将指定的本体词设置为 `is_deleted=true`, `is_selected=false`
  2. 查询关联的搜索词：`SELECT id FROM search_terms WHERE entity_word_id IN (...)`
  3. 批量软删除搜索词：`UPDATE search_terms SET is_deleted=true WHERE entity_word_id IN (...)`
- **数据一致性**：保证不会有搜索词引用已删除的本体词

#### 6.6.2 删除属性词时的级联
- **触发条件**：Stage 2 中删除属性词
- **级联操作**：
  1. 将指定的属性词设置为 `is_deleted=true`, `is_selected=false`
  2. 查询关联的搜索词：`SELECT id FROM search_terms WHERE attribute_id IN (...)`
  3. 批量软删除搜索词：`UPDATE search_terms SET is_deleted=true WHERE attribute_id IN (...)`

#### 6.6.3 状态回退时的数据清理
- **触发条件**：任务状态从 `combined` 回退到 `selected`
- **清理操作**：
  - 软删除所有搜索词：`UPDATE search_terms SET is_deleted=true WHERE task_id = ?`
  - 软删除所有本体词：`UPDATE entity_words SET is_deleted=true WHERE task_id = ?`
- **目的**：保证数据一致性，避免历史数据干扰

---

### 6.7 笛卡尔积上限保护规则 ✨

#### 6.7.1 上限设置
- **最大搜索词数量**：1000
- **计算公式**：`selected_attribute_count × selected_entity_word_count`

#### 6.7.2 验证时机
- API 4（生成搜索词）开始前
- 在查询已选属性词和本体词后立即验证

#### 6.7.3 超限处理
- **错误码**：`400 Bad Request`
- **错误提示**：`搜索词组合数量超过上限（当前：{attr_count} × {entity_count} = {total}，上限：1000），请减少属性词或本体词的选择数量`
- **不执行后续操作**：不进行任何数据库修改

#### 6.7.4 建议策略
- 如果超限，建议用户：
  1. 减少属性词选择（取消勾选不重要的属性词）
  2. 减少本体词选择（取消勾选不重要的本体词变体）
  3. 分批生成（拆分成多个任务）

---

### 6.8 空选择验证规则 ✨

#### 6.8.1 API 3（更新本体词选择）验证
- **验证条件**：`selected_count == 0 && new_entity_words.length == 0`
- **错误码**：`400 Bad Request`
- **错误提示**：`至少需要选择 1 个本体词或添加 1 个自定义本体词`

#### 6.8.2 验证时机
- 在更新选择状态之前
- 在计算 `selected_count` 之后

---

## 7. AI Prompt 设计

### 7.1 Prompt 文件信息

**文件名**: `entity_word_expert_v1.txt`
**存储路径**: `backend_v2/app/config/prompts/entity_word_expert_v1.txt`
**版本**: v1
**模型**: DeepSeek Chat
**提示词规模**: 约 350 行

---

### 7.2 Prompt 核心结构

```
1. 角色定义 (30行)
   - 专家身份
   - 任务说明

2. 核心概念 (60行)
   - 同义词定义和示例
   - 变体定义和5种类型

3. 扩展规则 (50行)
   - 规则1: 保持产品类型不变
   - 规则2: 覆盖用户搜索习惯
   - 规则3: 优先级排序
   - 规则4: 美式英语

4. 输出格式 (80行)
   - JSON 结构定义
   - 字段说明

5. 示例 (100行)
   - 3-5 个完整示例
   - 涵盖不同产品类型

6. 任务指令 (30行)
   - 动态参数 {entity_word}
   - 具体要求
```

---

### 7.3 Prompt 内容（完整版）

请查看独立文件：`entity_word_expert_v1.txt`（将在下一步创建）

**关键动态参数**：
- `{entity_word}` - 用户输入的本体词（运行时填充）

---

### 7.4 AI 响应格式

**AI 返回的 JSON 格式**（中文字段）：
```json
[
  {
    "本体词": "iphone 14 case",
    "词汇类型": "原词",
    "中文说明": "iPhone 14 手机壳（原始输入）",
    "适用场景": "用户标准搜索词",
    "推荐度": "✅",
    "搜索价值": "⭐⭐⭐⭐⭐"
  }
]
```

**后端转换为标准格式**（英文字段）：
```json
{
  "entity_word": "iphone 14 case",
  "type": "original",
  "translation": "iPhone 14 手机壳（原始输入）",
  "use_case": "用户标准搜索词",
  "recommended": true,
  "search_value": "high",
  "search_value_stars": 5
}
```

**字段映射表**：

| 中文字段 | 英文字段 | 转换逻辑 |
|---------|---------|---------|
| 本体词 | entity_word | 直接映射 |
| 词汇类型 | type | 原词→original, 同义词→synonym, 变体→variant |
| 中文说明 | translation | 直接映射 |
| 适用场景 | use_case | 直接映射 |
| 推荐度 | recommended | ✅→true, ⚠️→false |
| 搜索价值 | search_value + search_value_stars | ⭐⭐⭐⭐⭐→high(5), ⭐⭐⭐⭐→high(4), ⭐⭐⭐→medium(3) |

---

## 8. 技术架构

### 8.1 分层架构

```
┌─────────────────────────────────────────────────┐
│           API 层 (main.py)                      │
│  - POST .../entity-words/generate               │
│  - GET  .../entity-words                        │
│  - PUT  .../entity-words/selection              │
│  - POST .../search-terms                        │
│  - GET  .../search-terms                        │
│  - DELETE .../search-terms/batch                │
├─────────────────────────────────────────────────┤
│       数据验证层 (Pydantic Schemas)              │
│  - EntityWordGenerateRequest/Response           │
│  - EntityWordSelectionRequest/Response          │
│  - SearchTermRequest/Response                   │
├─────────────────────────────────────────────────┤
│          业务逻辑层 (CRUD)                       │
│  - crud/entity_word.py                          │
│  - crud/search_term.py                          │
├─────────────────────────────────────────────────┤
│        ORM 层 (SQLAlchemy Models)               │
│  - EntityWord (本体词表)                         │
│  - SearchTerm (搜索词表)                         │
├─────────────────────────────────────────────────┤
│          AI 服务层 (services)                    │
│  - EntityWordProvider (本体词生成服务)           │
├─────────────────────────────────────────────────┤
│      数据库连接层 (Database)                     │
│  - Session 管理                                  │
│  - 依赖注入                                      │
├─────────────────────────────────────────────────┤
│       数据库 (SQLite/PostgreSQL)                 │
│  - entity_words 表                              │
│  - search_terms 表                              │
└─────────────────────────────────────────────────┘
```

---

### 8.2 核心模块设计

#### 8.2.1 CRUD 模块

**文件**: `backend_v2/app/crud/entity_word.py`

**核心函数**:
```python
def create_entity_words_batch(db: Session, task_id: str, entity_words: List[Dict]) -> int:
    """批量创建本体词"""

def get_entity_words_by_task(db: Session, task_id: str, include_deleted: bool = False) -> List[EntityWord]:
    """查询任务的本体词列表"""

def update_entity_word_selection(db: Session, task_id: str, selected_ids: List[int]) -> int:
    """更新本体词选中状态"""

def add_custom_entity_word(db: Session, task_id: str, entity_word: str) -> EntityWord:
    """添加用户自定义本体词"""

def soft_delete_entity_words(db: Session, task_id: str, entity_word_ids: List[int]) -> int:
    """软删除本体词"""

def get_selected_count(db: Session, task_id: str) -> int:
    """查询选中的本体词数量"""
```

---

**文件**: `backend_v2/app/crud/search_term.py`

**核心函数**:
```python
def create_search_terms_batch(db: Session, task_id: str, search_terms: List[Dict]) -> int:
    """批量创建搜索词"""

def get_search_terms_by_task(db: Session, task_id: str, page: int = 1, page_size: int = 20,
                              filter_by_attribute: str = None, filter_by_entity: str = None,
                              include_deleted: bool = False) -> Tuple[List[SearchTerm], int]:
    """分页查询搜索词列表"""

def soft_delete_search_terms(db: Session, task_id: str, search_term_ids: List[int]) -> int:
    """批量软删除搜索词"""

def get_search_term_stats(db: Session, task_id: str) -> Dict:
    """获取搜索词统计信息"""
```

---

#### 8.2.2 AI 服务模块

**文件**: `backend_v2/app/services/entity_word_provider.py`

**类设计**:
```python
class EntityWordProvider:
    """本体词生成服务提供者"""

    def __init__(self, config: Dict, prompt_template: str):
        self.api_key = config["api_key"]
        self.api_base = config["api_base"]
        self.model = config["model"]
        self.prompt_template = prompt_template

    async def generate_entity_words(self, entity_word: str, max_count: int = 15) -> List[Dict]:
        """
        调用 AI 生成本体词变体

        Args:
            entity_word: 原始本体词
            max_count: 最大生成数量

        Returns:
            本体词列表（中文字段格式）
        """
        # 1. 填充 prompt 模板
        prompt = self.prompt_template.format(entity_word=entity_word)

        # 2. 调用 DeepSeek API
        response = await self._call_api(prompt)

        # 3. 解析响应（处理 markdown 代码块）
        entity_words = self._parse_response(response)

        # 4. 验证和过滤
        entity_words = self._validate_entity_words(entity_words, entity_word)

        # 5. 限制数量
        return entity_words[:max_count]

    def _parse_response(self, response: str) -> List[Dict]:
        """解析 AI 响应（处理 JSON 和 markdown）"""

    def _validate_entity_words(self, entity_words: List[Dict], original: str) -> List[Dict]:
        """验证本体词质量"""
```

---

#### 8.2.3 数据转换模块

**函数**: `convert_entity_word_to_standard()`

**功能**: 将 AI 返回的中文字段转换为标准英文字段

**实现**:
```python
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
    recommended = entity_word_data["推荐度"] == "✅"

    # 搜索价值转换
    stars_count = entity_word_data["搜索价值"].count("⭐")
    if stars_count >= 4:
        search_value = "high"
    elif stars_count == 3:
        search_value = "medium"
    else:
        search_value = "low"

    return {
        "entity_word": entity_word_data["本体词"],
        "type": type_mapping[entity_word_data["词汇类型"]],
        "translation": entity_word_data["中文说明"],
        "use_case": entity_word_data["适用场景"],
        "recommended": recommended,
        "search_value": search_value,
        "search_value_stars": stars_count
    }
```

---

### 8.3 性能优化

#### 8.3.1 批量操作
- 使用 `bulk_save_objects()` 批量插入
- 避免逐条插入导致的性能问题

**示例**:
```python
# ❌ 低效：逐条插入
for entity_word in entity_words:
    db.add(EntityWord(**entity_word))
    db.commit()

# ✅ 高效：批量插入
db_entity_words = [EntityWord(**ew) for ew in entity_words]
db.bulk_save_objects(db_entity_words)
db.commit()
```

#### 8.3.2 索引优化
- 在高频查询字段上建立索引
- 复合索引：`(task_id, is_deleted)`

#### 8.3.3 分页查询
- 搜索词列表支持分页（默认 20 条/页）
- 避免一次性加载大量数据

---

### 8.4 错误处理

#### 8.4.1 输入验证模块 ✨

**函数**: `validate_entity_word(entity_word: str) -> Tuple[bool, str]`

**验证规则**:
```python
import re

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
```

**使用时机**:
- API 1（生成本体词）- 验证用户输入的 `entity_word`
- API 3（更新选择）- 验证 `new_entity_words[].entity_word`

---

#### 8.4.2 AI 调用重试机制 ✨

**使用库**: `tenacity`

**重试策略**:
```python
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

class EntityWordProvider:

    @retry(
        stop=stop_after_attempt(3),           # 最多重试 3 次
        wait=wait_fixed(2),                    # 每次间隔 2 秒
        retry=retry_if_exception_type((TimeoutError, ConnectionError)),  # 只重试网络错误
        reraise=True                           # 最终失败时抛出异常
    )
    async def _call_api(self, prompt: str) -> str:
        """
        调用 DeepSeek API（带重试）

        重试条件：
        - TimeoutError（超时）
        - ConnectionError（连接失败）

        不重试条件：
        - 401 认证失败
        - 400 参数错误
        """
        response = await self.client.post(
            self.api_base,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            },
            timeout=30.0
        )

        if response.status_code == 401:
            raise AuthenticationError("API key 无效")

        if response.status_code == 400:
            raise ValidationError("请求参数错误")

        return response.json()["choices"][0]["message"]["content"]
```

**日志记录**:
```python
import logging
from tenacity import before_log, after_log

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    before=before_log(logger, logging.INFO),   # 重试前记录日志
    after=after_log(logger, logging.INFO)      # 重试后记录日志
)
async def _call_api(self, prompt: str) -> str:
    ...
```

---

#### 8.4.3 增强的降级策略 ✨

**完整流程**:
```python
async def generate_entity_words(self, entity_word: str, max_count: int = 15) -> List[Dict]:
    """生成本体词（带降级策略）"""

    # 1. 输入验证
    is_valid, error_msg = validate_entity_word(entity_word)
    if not is_valid:
        raise ValueError(error_msg)

    try:
        # 2. 尝试 AI 生成（带重试）
        entity_words = await self._call_api_and_parse(entity_word)

        # 3. 验证 AI 返回结果质量
        if len(entity_words) < 3:  # 至少应该有原词 + 2个变体
            logger.warning(f"AI 返回结果不足，启用增强降级策略")
            raise InsufficientResultsError("AI 返回结果不足")

        return entity_words[:max_count]

    except (TimeoutError, ConnectionError, AuthenticationError) as e:
        logger.error(f"AI 调用失败: {type(e).__name__} - {str(e)}")
        # 降级：返回增强的基础变体
        return self._get_enhanced_basic_variants(entity_word)

    except (JSONDecodeError, ValidationError) as e:
        logger.error(f"AI 响应解析失败: {str(e)}")
        # 降级：返回增强的基础变体
        return self._get_enhanced_basic_variants(entity_word)
```

**增强的基础变体生成规则** (5-8个变体):
```python
def _get_enhanced_basic_variants(self, entity_word: str) -> List[Dict]:
    """
    生成增强的基础变体（不依赖 AI）
    确保至少返回 5-8 个变体
    """
    variants = []

    # 1. 原词（必须）
    variants.append({
        "entity_word": entity_word,
        "type": "original",
        "translation": f"{entity_word}（原始输入）",
        "use_case": "用户标准搜索词",
        "recommended": True,
        "search_value": "high",
        "search_value_stars": 5
    })

    # 2. 去空格变体
    if " " in entity_word:
        no_space = entity_word.replace(" ", "")
        variants.append({
            "entity_word": no_space,
            "type": "variant",
            "translation": "去空格变体",
            "use_case": "用户快速输入",
            "recommended": False,
            "search_value": "medium",
            "search_value_stars": 3
        })

    # 3. 单复数变体
    if entity_word.endswith("s"):
        singular = entity_word[:-1]
        variants.append({
            "entity_word": singular,
            "type": "variant",
            "translation": "单数形式",
            "use_case": "用户搜索单个商品",
            "recommended": True,
            "search_value": "medium",
            "search_value_stars": 3
        })
    else:
        plural = entity_word + "s"
        variants.append({
            "entity_word": plural,
            "type": "variant",
            "translation": "复数形式",
            "use_case": "用户搜索多个商品",
            "recommended": True,
            "search_value": "medium",
            "search_value_stars": 3
        })

    # 4. 连字符变体
    if " " in entity_word:
        hyphen_variant = entity_word.replace(" ", "-")
        variants.append({
            "entity_word": hyphen_variant,
            "type": "variant",
            "translation": "连字符形式",
            "use_case": "某些平台的搜索习惯",
            "recommended": False,
            "search_value": "low",
            "search_value_stars": 2
        })

    # 5. 词序调整（介词组合）
    words = entity_word.split()
    if len(words) >= 2:
        # 示例：iphone 14 case → case for iphone 14
        last_word = words[-1]
        rest = " ".join(words[:-1])
        reordered = f"{last_word} for {rest}"
        variants.append({
            "entity_word": reordered,
            "type": "variant",
            "translation": "介词组合变体",
            "use_case": "自然语言搜索习惯",
            "recommended": True,
            "search_value": "medium",
            "search_value_stars": 3
        })

    # 6. 缩写变体（如果有数字）
    if any(char.isdigit() for char in entity_word):
        # 示例：iphone 14 case → 14 case
        abbreviated = " ".join([w for w in words if any(c.isdigit() for c in w) or w == words[-1]])
        if abbreviated != entity_word:
            variants.append({
                "entity_word": abbreviated,
                "type": "variant",
                "translation": "简写形式",
                "use_case": "用户省略品牌名",
                "recommended": False,
                "search_value": "low",
                "search_value_stars": 2
            })

    # 7. 首字母大写变体
    capitalized = entity_word.title()
    if capitalized != entity_word:
        variants.append({
            "entity_word": capitalized,
            "type": "variant",
            "translation": "首字母大写形式",
            "use_case": "品牌名大写搜索",
            "recommended": False,
            "search_value": "low",
            "search_value_stars": 2
        })

    # 8. 全小写变体
    if entity_word != entity_word.lower():
        variants.append({
            "entity_word": entity_word.lower(),
            "type": "variant",
            "translation": "全小写形式",
            "use_case": "标准搜索习惯",
            "recommended": True,
            "search_value": "medium",
            "search_value_stars": 3
        })

    return variants
```

---

#### 8.4.4 数据库操作失败
- 使用事务（Transaction）保证原子性
- 失败时回滚（Rollback）

```python
try:
    db.bulk_save_objects(search_terms)
    db.commit()
except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail="数据库保存失败")
```

---

## 9. 测试用例

### 9.1 测试策略

**测试环境**: Replit
**数据库**: SQLite
**测试数据**: 基于 Stage 2 完成的任务

---

### 9.2 测试用例列表

#### 测试用例 1: 生成本体词变体

**前提条件**:
- 任务 `task_id` 已完成 Stage 2
- 状态为 `selected`
- 本体词: `iphone 14 case`

**测试步骤**:
```bash
curl -X POST {BASE_URL}/api/stage3/tasks/{task_id}/entity-words/generate \
  -H "Content-Type: application/json" \
  -d '{
    "options": {
      "max_count": 15
    }
  }'
```

**预期结果**:
- 状态码: `200 OK`
- 返回 8-15 个本体词
- 包含原词 `iphone 14 case`
- 包含至少 2 个同义词（如 `cover`, `shell`）
- 包含至少 3 个变体（如 `iphone14 case`, `case for iphone 14`）
- `metadata.total_count` = 实际生成数量
- 任务状态更新为 `entity_expanded`

**验证点**:
- [ ] AI 生成成功
- [ ] 数据保存到 `entity_words` 表
- [ ] 所有本体词默认 `is_selected=true`
- [ ] 类型分布合理（原词1个、同义词2-4个、变体5-10个）
- [ ] 搜索价值星级正确

---

#### 测试用例 2: 查询本体词列表

**前提条件**: 测试用例 1 已完成

**测试步骤**:
```bash
curl {BASE_URL}/api/stage3/tasks/{task_id}/entity-words
```

**预期结果**:
- 状态码: `200 OK`
- 返回所有生成的本体词
- 不包含已删除的本体词
- 按搜索价值星级降序排序

**验证点**:
- [ ] 数据与测试用例 1 一致
- [ ] 所有字段完整

---

#### 测试用例 3: 更新本体词选择

**前提条件**: 测试用例 1 已完成

**测试步骤**:
```bash
curl -X PUT {BASE_URL}/api/stage3/tasks/{task_id}/entity-words/selection \
  -H "Content-Type: application/json" \
  -d '{
    "selected_entity_word_ids": [1, 2, 3, 4, 5],
    "new_entity_words": [
      {"entity_word": "iphone 14 protective case"}
    ],
    "deleted_entity_word_ids": [10]
  }'
```

**预期结果**:
- 状态码: `200 OK`
- `metadata.selected_count` = 6（5个选中 + 1个新增）
- `metadata.changes.selected` = 5
- `metadata.changes.added` = 1
- `metadata.changes.deleted` = 1
- 任务状态更新为 `entity_selected`

**验证点**:
- [ ] 选中状态更新正确
- [ ] 新增的本体词保存成功（`source='user'`, `is_selected=true`）
- [ ] 删除的本体词标记为 `is_deleted=true`

---

#### 测试用例 4: 生成搜索词组合

**前提条件**:
- 测试用例 3 已完成
- Stage 2 有 15 个已选属性词
- Stage 3.2 有 6 个已选本体词

**测试步骤**:
```bash
curl -X POST {BASE_URL}/api/stage3/tasks/{task_id}/search-terms \
  -H "Content-Type: application/json" \
  -d '{
    "options": {
      "max_length": 80,
      "deduplicate": true
    }
  }'
```

**预期结果**:
- 状态码: `200 OK`
- `metadata.total_terms` = 90（15 × 6）
- `metadata.valid_terms` = 90（所有搜索词长度 ≤ 80）
- 返回所有搜索词列表
- 任务状态更新为 `combined`

**验证点**:
- [ ] 组合数量正确（属性词数 × 本体词数）
- [ ] 每个搜索词格式正确（`attribute + 空格 + entity`）
- [ ] 字符长度计算准确
- [ ] 没有重复的搜索词
- [ ] 数据保存到 `search_terms` 表

---

#### 测试用例 5: 查询搜索词列表（分页）

**前提条件**: 测试用例 4 已完成

**测试步骤**:
```bash
curl "{BASE_URL}/api/stage3/tasks/{task_id}/search-terms?page=1&page_size=20"
```

**预期结果**:
- 状态码: `200 OK`
- 返回 20 个搜索词
- `pagination.page` = 1
- `pagination.page_size` = 20
- `pagination.total_pages` = 5（90 / 20 = 4.5，向上取整）
- `pagination.total_count` = 90

**验证点**:
- [ ] 分页计算正确
- [ ] 数据完整

---

#### 测试用例 6: 筛选搜索词（按属性词）

**前提条件**: 测试用例 4 已完成

**测试步骤**:
```bash
curl "{BASE_URL}/api/stage3/tasks/{task_id}/search-terms?filter_by_attribute=cute"
```

**预期结果**:
- 状态码: `200 OK`
- 只返回包含属性词 `cute` 的搜索词（6 个）
- 所有返回的搜索词的 `attribute_word` = `cute`

**验证点**:
- [ ] 筛选正确
- [ ] 数量正确

---

#### 测试用例 7: 批量删除搜索词

**前提条件**: 测试用例 4 已完成

**测试步骤**:
```bash
curl -X DELETE {BASE_URL}/api/stage3/tasks/{task_id}/search-terms/batch \
  -H "Content-Type: application/json" \
  -d '{
    "search_term_ids": [1, 5, 10, 15]
  }'
```

**预期结果**:
- 状态码: `200 OK`
- `deleted_count` = 4
- `remaining_count` = 86

**验证点**:
- [ ] 指定的搜索词标记为 `is_deleted=true`
- [ ] 其他搜索词不受影响
- [ ] 再次查询列表时不包含已删除的搜索词

---

#### 测试用例 8: 验证数据持久化

**前提条件**: 所有前面的测试用例已完成

**测试步骤**:
1. 关闭浏览器/客户端
2. 重新访问 API

```bash
curl {BASE_URL}/api/stage3/tasks/{task_id}/entity-words
curl {BASE_URL}/api/stage3/tasks/{task_id}/search-terms
```

**预期结果**:
- 所有数据保持不变
- 选中状态保持不变
- 删除状态保持不变

**验证点**:
- [ ] 数据持久化成功
- [ ] 任务可恢复

---

### 9.3 测试矩阵

| 测试用例 | 功能模块 | 优先级 | 状态 |
|---------|---------|--------|------|
| 测试1 | 本体词生成 | P0 | 待测试 |
| 测试2 | 本体词查询 | P0 | 待测试 |
| 测试3 | 本体词选择 | P0 | 待测试 |
| 测试4 | 搜索词组合 | P0 | 待测试 |
| 测试5 | 搜索词查询（分页） | P0 | 待测试 |
| 测试6 | 搜索词筛选 | P1 | 待测试 |
| 测试7 | 批量删除 | P1 | 待测试 |
| 测试8 | 数据持久化 | P0 | 待测试 |

---

## 10. 实施计划

### 10.1 开发任务分解

#### 阶段 1: 数据库和模型（2-3 天）
- [ ] 创建 `entity_words` 表（迁移脚本）
- [ ] 创建 `search_terms` 表（迁移脚本）
- [ ] 定义 ORM 模型（`models_db.py`）
- [ ] 定义 Pydantic 模型（`schemas/stage3.py`）
- [ ] 测试数据库表创建

#### 阶段 2: 本体词生成（3-4 天）
- [ ] 创建 AI Prompt 文件（`entity_word_expert_v1.txt`）
- [ ] 实现 `EntityWordProvider` 服务
  - [ ] 实现 AI 调用重试机制（tenacity，3次，间隔2秒）✨
  - [ ] 实现增强的降级策略（5-8个基础变体）✨
- [ ] 实现输入验证函数（`validate_entity_word`）✨
- [ ] 实现数据转换函数（中文→英文）
- [ ] 实现 CRUD 函数（`crud/entity_word.py`）
- [ ] 实现 API 端点 1（生成本体词）
  - [ ] 添加状态前置条件验证 ✨
  - [ ] 集成输入验证 ✨
  - [ ] 添加 concept 字段处理 ✨
- [ ] 实现 API 端点 2（查询本体词）
- [ ] 单元测试

#### 阶段 3: 本体词筛选（2-3 天）
- [ ] 实现 API 端点 3（更新本体词选择）
  - [ ] 添加空选择验证 ✨
  - [ ] 集成输入验证（自定义本体词）✨
  - [ ] 实现级联软删除逻辑 ✨
- [ ] 实现添加自定义本体词逻辑
- [ ] 实现软删除逻辑
- [ ] 任务状态更新逻辑
- [ ] 单元测试

#### 阶段 4: 搜索词组合（3-4 天）
- [ ] 实现笛卡尔积组合算法
  - [ ] 添加笛卡尔积上限验证（1000）✨
- [ ] 实现长度验证逻辑
- [ ] 实现去重逻辑
- [ ] 实现幂等操作逻辑 ✨
  - [ ] 物理删除已软删除记录
  - [ ] 软删除现有有效记录
- [ ] 实现 CRUD 函数（`crud/search_term.py`）
- [ ] 实现 API 端点 4（生成搜索词）
  - [ ] 添加状态前置条件验证 ✨
  - [ ] 集成笛卡尔积上限保护 ✨
  - [ ] 实现幂等操作 ✨
- [ ] 实现 API 端点 5（查询搜索词）
- [ ] 实现分页逻辑
- [ ] 实现筛选逻辑
- [ ] 单元测试

#### 阶段 5: 搜索词管理（1-2 天）
- [ ] 实现 API 端点 6（批量删除）
  - [ ] 添加原子性验证（先验证所有ID）✨
  - [ ] 实现事务批量删除 ✨
- [ ] 单元测试

#### 阶段 6: 集成测试和部署（2-3 天）
- [ ] 端到端测试（8 个测试用例）
- [ ] 性能测试（大数据集）
- [ ] 错误处理测试
- [ ] 部署到 Replit
- [ ] 文档更新

---

### 10.2 时间估算

| 阶段 | 工作量 | 风险 |
|------|--------|------|
| 阶段 1 | 2-3 天 | 低 |
| 阶段 2 | 3-4 天 | 中（AI 调用） |
| 阶段 3 | 2-3 天 | 低 |
| 阶段 4 | 3-4 天 | 中（复杂度） |
| 阶段 5 | 1-2 天 | 低 |
| 阶段 6 | 2-3 天 | 中（集成） |
| **总计** | **13-19 天** | - |

**预计完成时间**: 3-4 周

---

### 10.3 里程碑

| 里程碑 | 交付物 | 完成标准 |
|--------|--------|---------|
| M1: 数据库就绪 | 2个新表创建完成 | 表结构正确，索引创建成功 |
| M2: 本体词生成 | AI 生成功能可用 | 测试用例 1-2 通过 |
| M3: 本体词筛选 | 筛选功能可用 | 测试用例 3 通过 |
| M4: 搜索词组合 | 组合功能可用 | 测试用例 4-6 通过 |
| M5: 完整功能 | 所有 API 可用 | 所有测试用例通过 |
| M6: 上线就绪 | 部署到生产环境 | 性能和稳定性验证 |

---

### 10.4 风险和缓解

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|---------|
| AI 生成质量不稳定 | 高 | 中 | 实现降级策略，提供基础变体 |
| 大数据集性能问题 | 中 | 中 | 使用批量操作、分页、索引优化 |
| 数据库迁移失败 | 高 | 低 | 提前备份，使用 Alembic 管理迁移 |
| API 响应超时 | 中 | 低 | 设置合理的超时时间，异步处理 |

---

## 附录

### A. 术语表

| 术语 | 英文 | 说明 |
|------|------|------|
| 本体词 | Product Entity Term | 描述"商品是什么"的核心词汇 |
| 属性词 | Attribute Term | 描述"商品什么样"的修饰词汇 |
| 同义词 | Synonym | 意思相同的不同表达 |
| 变体 | Variant | 形式上的变化（空格、单复数等） |
| 搜索词 | Search Term | 属性词 + 本体词组合的完整关键词 |
| 笛卡尔积 | Cartesian Product | 每个属性词 × 每个本体词 |
| 软删除 | Soft Delete | 标记为删除，不物理删除 |

---

### B. 相关文档

- **Stage 1 需求文档**: `项目需求文档.md` (第2章)
- **Stage 2 实施文档**: `Stage2实施文档.md`
- **AI Prompt 文件**: `entity_word_expert_v1.txt`（待创建）
- **数据库设计**: 本文档第4章
- **API 文档**: 本文档第5章

---

### C. 开发环境

**后端**:
- Python 3.9+
- FastAPI 0.121.0
- SQLAlchemy 2.0.23
- DeepSeek API

**数据库**:
- 开发环境: SQLite
- 生产环境: PostgreSQL

**部署**:
- Replit（测试环境）
- 其他云平台（生产环境）

---

### D. Git 分支策略

**分支命名**:
```
feature/stage3-entity-words      # 本体词功能
feature/stage3-search-terms      # 搜索词功能
feature/stage3-integration       # 集成和测试
```

**合并策略**:
1. 开发分支 → `feature/stage3-implementation`
2. 测试通过后 → `main`

---

---

## 11. 优化点汇总 ✨

本章节汇总了所有在需求评估阶段确认并加入的优化点（标记 ✨）。

### 11.1 数据库设计优化（3项）

#### 11.1.1 entity_words 表增加 concept 字段
**问题**: 原设计缺少原始属性概念字段，导致无法追溯本体词来源
**方案**: 添加 `concept VARCHAR(200) NOT NULL` 字段，关联 tasks.concept
**影响范围**: 数据库表结构、API 1（生成本体词）
**文档位置**: 4.1 节、5.2 API 1

#### 11.1.2 search_terms 唯一性约束冲突处理
**问题**: 重新生成时，软删除的记录会导致唯一索引冲突
**方案**: 重新生成前，先物理删除（DELETE）已软删除的记录
**影响范围**: API 4（生成搜索词）
**文档位置**: 4.2 节、5.2 API 4

#### 11.1.3 状态回退时的数据清理
**问题**: 任务状态回退时，历史数据可能导致不一致
**方案**: 状态回退到 `selected` 时，自动软删除所有搜索词和本体词
**影响范围**: 任务状态管理逻辑
**文档位置**: 6.6.3 节

---

### 11.2 API 设计优化（4项）

#### 11.2.1 API 4（生成搜索词）幂等性保障
**问题**: 多次调用会生成重复数据
**方案**: 生成前先软删除现有有效记录，物理删除已软删除记录
**影响范围**: API 4 处理逻辑
**文档位置**: 5.2 API 4、6.7 节

#### 11.2.2 API 6（批量删除）事务保障
**问题**: 部分 ID 无效时可能导致部分删除
**方案**: 先验证所有 ID，再在单个事务中批量删除（原子操作）
**影响范围**: API 6 处理逻辑
**文档位置**: 5.2 API 6、10.1 阶段5

#### 11.2.3 状态前置条件验证
**问题**: 在错误状态下调用 API 会导致数据不一致
**方案**:
- API 1（生成本体词）：只允许 `selected`, `entity_expanded`, `entity_selected`, `combined` 状态
- API 4（生成搜索词）：只允许 `entity_selected`, `combined` 状态
**影响范围**: API 1、API 4
**文档位置**: 5.2 节、6.5 节、10.1 阶段2和4

#### 11.2.4 空选择验证
**问题**: 用户可能取消所有选择导致后续生成失败
**方案**: API 3（更新选择）时验证至少选择 1 个本体词
**影响范围**: API 3 处理逻辑
**文档位置**: 5.2 API 3、6.8 节、10.1 阶段3

---

### 11.3 业务逻辑完善（3项）

#### 11.3.1 笛卡尔积上限保护
**问题**: 大量属性词 × 大量本体词可能导致性能问题
**方案**: 设置上限 1000，超限时拒绝生成并提示用户减少选择
**影响范围**: API 4（生成搜索词）
**文档位置**: 5.2 API 4、6.7 节、10.1 阶段4

#### 11.3.2 级联软删除
**问题**: 删除本体词或属性词时，相关搜索词变成孤儿数据
**方案**:
- 删除本体词 → 级联软删除相关搜索词
- 删除属性词 → 级联软删除相关搜索词
**影响范围**: API 3（更新本体词选择）、Stage 2 属性词删除
**文档位置**: 5.2 API 3、6.6 节、10.1 阶段3

#### 11.3.3 输入验证
**问题**: 不合法的本体词可能导致 AI 生成失败或数据异常
**方案**: 验证规则：
- 长度 ≤ 200 字符
- 只允许英文、数字、空格、连字符
- 不允许连续空格
**影响范围**: API 1（生成本体词）、API 3（添加自定义本体词）
**文档位置**: 5.2 API 1&3、8.4.1 节、10.1 阶段2和3

---

### 11.4 性能优化（2项）

#### 11.4.1 批量操作性能
**问题**: 大批量操作可能性能不佳
**方案**: 使用 SQLAlchemy `bulk_save_objects()` 而非逐条插入
**影响范围**: 所有批量插入操作
**文档位置**: 8.3.1 节

#### 11.4.2 软删除数据清理
**问题**: 软删除数据累积可能影响性能和唯一索引
**方案**: 重新生成前物理删除已软删除的记录
**影响范围**: API 4（生成搜索词）
**文档位置**: 4.2 节、5.2 API 4

---

### 11.5 AI 服务优化（3项）

#### 11.5.1 AI 调用重试机制
**问题**: 网络抖动或临时故障导致生成失败
**方案**: 使用 tenacity 库，最多重试 3 次，间隔 2 秒
**影响范围**: EntityWordProvider 服务
**文档位置**: 8.4.2 节、10.1 阶段2

#### 11.5.2 增强的降级策略
**问题**: AI 完全失败时用户体验差
**方案**: 提供 5-8 个高质量基础变体（包含原词、单复数、连字符、介词组合等）
**影响范围**: EntityWordProvider 服务
**文档位置**: 8.4.3 节、10.1 阶段2

#### 11.5.3 输入格式验证
**问题**: 不合法输入可能导致 AI 调用浪费或返回无效结果
**方案**: 调用 AI 前先验证输入格式
**影响范围**: API 1（生成本体词）
**文档位置**: 8.4.1 节、10.1 阶段2

---

### 11.6 优化点统计

| 类别 | 优化项数量 | 优先级 |
|------|----------|--------|
| 数据库设计 | 3 | 高 |
| API 设计 | 4 | 高 |
| 业务逻辑 | 3 | 高 |
| 性能优化 | 2 | 中 |
| AI 服务 | 3 | 高 |
| **总计** | **15** | - |

**实施状态**: 全部已纳入需求文档和实施计划
**标识方式**: 文档中所有优化点均标记 ✨ 符号
**评审结果**: 已获用户确认，暂不实施的优化点已明确排除

---

**文档编写**: AI 助手
**审核人**: 产品负责人
**批准人**: 技术负责人
**最后更新**: 2025-11-06
**文档版本**: v1.1 ✨

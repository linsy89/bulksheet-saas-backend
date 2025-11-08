# Stage 3 开发总结文档

## 📋 目录
- [功能概述](#功能概述)
- [API 端点](#api-端点)
- [数据模型](#数据模型)
- [核心问题与解决方案](#核心问题与解决方案)
- [架构设计](#架构设计)
- [优化点](#优化点)
- [测试验证](#测试验证)
- [文件清单](#文件清单)
- [经验教训](#经验教训)

---

## 功能概述

### Stage 3：本体词扩展与搜索词组合

**核心目标**：从用户选中的属性词和本体词生成最终的搜索词列表。

**工作流程**：
```
Stage 1: 生成属性词（15个）
    ↓
Stage 2: 用户选择属性词（6个）
    ↓
Stage 3.1: AI 生成本体词变体（12个）
    ↓
Stage 3.2: 用户选择本体词（4个）
    ↓
Stage 3.3: 生成搜索词（6 × 4 = 24个）
```

**示例**：
```
属性词：waterproof, splash-proof, ip68
本体词：phone case, phone cover, protective case
      ↓
搜索词：waterproof phone case
      waterproof phone cover
      waterproof protective case
      splash-proof phone case
      ...（共 9 个组合）
```

---

## API 端点

### API 1: 生成本体词变体
**端点**：`POST /api/stage3/tasks/{task_id}/entity-words/generate`

**功能**：使用 AI 生成本体词的同义词和变体

**请求体**：
```json
{
  "entity_word": "phone case",
  "max_count": 15,
  "options": {
    "enable_ai": true
  }
}
```

**响应**：
```json
{
  "task_id": "xxx",
  "entity_words": [
    {
      "id": 1,
      "entity_word": "phone case",
      "type": "original",
      "translation": "手机壳（原始输入）",
      "use_case": "用户标准搜索词",
      "search_value": "high",
      "search_value_stars": 5,
      "recommended": true,
      "source": "ai",
      "is_selected": true
    },
    {
      "id": 2,
      "entity_word": "phone cover",
      "type": "synonym",
      "translation": "手机保护套",
      "use_case": "用户常用替代表达",
      "search_value": "high",
      "search_value_stars": 5,
      "recommended": true,
      "source": "ai",
      "is_selected": true
    }
  ],
  "metadata": {
    "total_count": 12,
    "selected_count": 12,
    "type_distribution": {
      "original": 1,
      "synonym": 3,
      "variant": 8
    }
  },
  "status": "entity_expanded",
  "updated_at": "2025-11-06T17:13:41"
}
```

**特性**：
- ✅ AI 生成（DeepSeek API）
- ✅ 重试机制（3 次，间隔 2 秒）
- ✅ 降级策略（AI 失败时返回基础变体）
- ✅ 幂等操作（重复调用会先删除旧数据）

---

### API 2: 查询本体词列表
**端点**：`GET /api/stage3/tasks/{task_id}/entity-words`

**查询参数**：
- `include_deleted` (boolean): 是否包含已删除的本体词

**响应**：
```json
{
  "task_id": "xxx",
  "entity_words": [...],
  "metadata": {
    "total_count": 12,
    "selected_count": 12,
    "type_distribution": {
      "original": 1,
      "synonym": 3,
      "variant": 8
    }
  }
}
```

**特性**：
- ✅ 按搜索价值星级降序排序
- ✅ 支持软删除过滤

---

### API 3: 更新本体词选择
**端点**：`PUT /api/stage3/tasks/{task_id}/entity-words/selection`

**请求体**：
```json
{
  "selected_entity_word_ids": [1, 3, 5],
  "new_entity_words": [
    {
      "entity_word": "phone cover",
      "type": "synonym",
      "translation": "手机保护套",
      "use_case": "用户自定义",
      "search_value": "high",
      "search_value_stars": 5,
      "recommended": true
    }
  ],
  "deleted_entity_word_ids": [7, 8]
}
```

**响应**：
```json
{
  "task_id": "xxx",
  "status": "entity_selected",
  "updated_at": "2025-11-06T17:14:00",
  "metadata": {
    "selected_count": 4,
    "total_count": 11,
    "changes": {
      "selected": 3,
      "added": 1,
      "deleted": 2
    }
  }
}
```

**特性**：
- ✅ 支持用户自定义添加
- ✅ 软删除机制
- ✅ 级联删除（删除本体词时，关联的搜索词也被删除）

---

### API 4: 生成搜索词
**端点**：`POST /api/stage3/tasks/{task_id}/search-terms`

**请求体**：
```json
{
  "options": {
    "max_length": 80
  }
}
```

**响应**：
```json
{
  "task_id": "xxx",
  "search_terms": [
    {
      "id": 1,
      "term": "waterproof phone case",
      "attribute_word": "waterproof",
      "entity_word": "phone case",
      "attribute_id": 1,
      "entity_word_id": 1,
      "length": 23,
      "is_valid": true
    }
  ],
  "metadata": {
    "total_terms": 24,
    "valid_terms": 24,
    "invalid_terms": 0
  },
  "status": "combined",
  "updated_at": "2025-11-06T17:15:00"
}
```

**特性**：
- ✅ 笛卡尔积生成（attributes × entity_words）
- ✅ 长度验证（≤ 80 字符）
- ✅ 幂等操作（删除旧数据后重新生成）

---

### API 5: 查询搜索词（分页）
**端点**：`GET /api/stage3/tasks/{task_id}/search-terms`

**查询参数**：
- `page` (int): 页码（从 1 开始）
- `page_size` (int): 每页数量
- `filter_by_attribute` (string): 按属性词过滤
- `filter_by_entity` (string): 按本体词过滤
- `include_deleted` (boolean): 是否包含已删除

**响应**：
```json
{
  "task_id": "xxx",
  "search_terms": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 24,
    "total_pages": 2
  },
  "metadata": {
    "total_terms": 24,
    "valid_terms": 24,
    "invalid_terms": 0
  }
}
```

**特性**：
- ✅ 分页查询
- ✅ 多维度过滤

---

### API 6: 批量删除搜索词
**端点**：`DELETE /api/stage3/tasks/{task_id}/search-terms/batch`

**请求体**：
```json
{
  "search_term_ids": [1, 5, 10]
}
```

**响应**：
```json
{
  "task_id": "xxx",
  "deleted_count": 3,
  "remaining_count": 21,
  "message": "已成功删除 3 个搜索词"
}
```

**特性**：
- ✅ 原子操作（删除前验证所有 ID 存在）
- ✅ 事务性批量删除

---

## 数据模型

### EntityWord（本体词表）

```python
class EntityWord(Base):
    __tablename__ = "entity_words"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.task_id"), nullable=False, index=True)
    entity_word = Column(String, nullable=False)           # 本体词文本
    concept = Column(String, nullable=False)               # 原始概念
    type = Column(String, nullable=False)                  # original/synonym/variant
    translation = Column(String)                           # 中文说明
    use_case = Column(String)                             # 适用场景
    search_value = Column(String, nullable=False)          # high/medium/low
    search_value_stars = Column(Integer, nullable=False)   # 1-5 星
    recommended = Column(Boolean, default=True)            # 是否推荐
    source = Column(String, default="ai")                  # ai/user
    is_selected = Column(Boolean, default=False)           # 是否选中
    is_deleted = Column(Boolean, default=False)            # 软删除标记
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**索引**：
- `task_id` (index)
- `is_deleted` (过滤查询)
- `is_selected` (过滤查询)

---

### SearchTerm（搜索词表）

```python
class SearchTerm(Base):
    __tablename__ = "search_terms"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, ForeignKey("tasks.task_id"), nullable=False, index=True)
    attribute_id = Column(Integer, ForeignKey("task_attributes.id"), nullable=False)
    entity_word_id = Column(Integer, ForeignKey("entity_words.id"), nullable=False)
    term = Column(String, nullable=False)                  # 完整搜索词
    attribute_word = Column(String, nullable=False)        # 属性词文本（冗余）
    entity_word = Column(String, nullable=False)           # 本体词文本（冗余）
    length = Column(Integer, nullable=False)               # 字符长度
    is_valid = Column(Boolean, default=True)               # 是否有效（长度 ≤ 80）
    is_deleted = Column(Boolean, default=False)            # 软删除标记
    created_at = Column(DateTime, default=datetime.utcnow)
```

**索引**：
- `task_id` (index)
- `attribute_id, entity_word_id` (复合索引，用于级联删除)

---

## 核心问题与解决方案

### 问题 1：Prompt 文件花括号导致 KeyError

**现象**：
```
❌ AI 生成失败: KeyError - '\n    "本体词"'
❌ 只返回 5 个基础变体（降级策略）
```

**根本原因**：
```python
# entity_word_provider.py:348
prompt = self.prompt_template.format(entity_word=entity_word)
```

Prompt 文件包含大量 JSON 示例：
```json
{
  "本体词": "iphone 14 case",
  "词汇类型": "原词"
}
```

Python `.format()` 把 `{` 和 `}` 当作变量占位符，找不到 `"本体词"` 变量，报 KeyError。

**解决方案**：

转义所有 JSON 花括号：
```json
{{
  "本体词": "iphone 14 case",
  "词汇类型": "原词"
}}
```

保留真正的变量：
```
**本体词**：{entity_word}
```

**修改文件**：
- `app/config/prompts/entity_word_expert_v1.txt`（56 处修改）

**验证结果**：

修复前（降级策略）：
```json
{
  "total_count": 5,
  "type_distribution": {"original": 1, "variant": 4}
}
```

修复后（AI 成功）：
```json
{
  "total_count": 12,
  "type_distribution": {"original": 1, "synonym": 3, "variant": 8}
}
```

---

### 问题 2：为什么 attribute_expert_v1.txt 没有这个问题？

**答案**：`attribute_expert_v1.txt` 在创建时已经正确转义了花括号。

**时间线**：
1. `11e5275`：创建 `attribute_expert_v1.txt`，花括号已转义 ✅
2. `9f53cea`：创建 `entity_word_expert_v1.txt`，忘记转义 ❌
3. `f948e15`：修复 `entity_word_expert_v1.txt` ✅

**经验教训**：知识没有传递，在第二次实现时重新犯了同样的错误。

---

## 架构设计

### AI 服务层

**EntityWordProvider**：
```python
class EntityWordProvider:
    def __init__(self, api_key: str, api_base: str, prompt_template: str):
        self.api_key = api_key
        self.api_base = api_base
        self.model = "deepseek-chat"
        self.prompt_template = prompt_template

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def _call_api(self, prompt: str) -> str:
        """调用 DeepSeek API（带重试）"""
        # 使用 aiohttp 调用 API
        # 超时设置：90 秒

    def _parse_response(self, response: str) -> List[Dict]:
        """解析 AI 响应（处理 JSON 和 markdown 代码块）"""
        # 1. 尝试直接解析 JSON
        # 2. 尝试提取 markdown 代码块中的 JSON
        # 3. 尝试查找任何 JSON 数组

    def _validate_entity_words(self, entity_words: List[Dict], original: str) -> List[Dict]:
        """验证本体词质量"""
        # 检查必填字段
        # 检查本体词格式（长度、字符）

    def _get_enhanced_basic_variants(self, entity_word: str) -> List[Dict]:
        """生成增强的基础变体（降级策略）"""
        # 1. 原词
        # 2. 去空格变体
        # 3. 单复数变体
        # 4. 连字符变体
        # 5. 词序调整（介词组合）
        # 6. 缩写变体
        # 7. 全小写变体

    async def generate_entity_words(self, entity_word: str, max_count: int = 15) -> List[Dict]:
        """生成本体词（带降级策略）"""
        try:
            # 1. 输入验证
            # 2. 尝试 AI 生成（带重试）
            # 3. 解析响应
            # 4. 验证结果
            # 5. 检查结果数量
            # 6. 转换为标准格式
            return entity_words[:max_count]
        except Exception as e:
            # 降级：返回增强的基础变体
            return self._get_enhanced_basic_variants(entity_word)[:max_count]
```

---

### CRUD 层

**entity_word.py**：
```python
def create_entity_words_batch(db, task_id, concept, entity_words, source="ai") -> int
def get_entity_words_by_task(db, task_id, include_deleted=False) -> List[EntityWord]
def update_entity_word_selection(db, task_id, selected_ids, new_entity_words, deleted_ids, concept) -> Tuple[int, int, int]
def get_selected_count(db, task_id) -> int
def get_entity_word_stats(db, task_id) -> Dict
def get_selected_entity_words(db, task_id) -> List[EntityWord]
def soft_delete_all_entity_words(db, task_id) -> int
```

**search_term.py**：
```python
def create_search_terms_batch(db, task_id, search_terms) -> int
def get_search_terms_by_task(db, task_id, page=1, page_size=20, filter_by_attribute=None, filter_by_entity=None, include_deleted=False) -> Tuple[List[SearchTerm], int]
def soft_delete_search_terms(db, task_id, search_term_ids) -> int
def get_search_term_stats(db, task_id) -> Dict
def get_remaining_count(db, task_id) -> int
def delete_existing_search_terms(db, task_id) -> None
def soft_delete_all_search_terms(db, task_id) -> int
```

---

### API 层（main.py）

**路由定义**：
```python
# Stage 3 API: 本体词生成与搜索词组合

@app.post("/api/stage3/tasks/{task_id}/entity-words/generate")
async def generate_entity_words(task_id: str, request: EntityWordGenerateRequest, db: Session = Depends(get_db))

@app.get("/api/stage3/tasks/{task_id}/entity-words")
async def get_entity_words(task_id: str, include_deleted: bool = False, db: Session = Depends(get_db))

@app.put("/api/stage3/tasks/{task_id}/entity-words/selection")
async def update_entity_word_selection(task_id: str, request: EntityWordSelectionRequest, db: Session = Depends(get_db))

@app.post("/api/stage3/tasks/{task_id}/search-terms")
async def generate_search_terms(task_id: str, request: SearchTermGenerateRequest, db: Session = Depends(get_db))

@app.get("/api/stage3/tasks/{task_id}/search-terms")
async def get_search_terms(task_id: str, page: int = 1, page_size: int = 20, filter_by_attribute: str = None, filter_by_entity: str = None, include_deleted: bool = False, db: Session = Depends(get_db))

@app.delete("/api/stage3/tasks/{task_id}/search-terms/batch")
async def batch_delete_search_terms(task_id: str, request: SearchTermBatchDeleteRequest, db: Session = Depends(get_db))
```

---

## 优化点

### 1. AI 服务降级策略
**实现**：AI 调用失败时自动返回基础变体

**代码**：
```python
try:
    entity_words = await self._call_api(prompt)
except Exception as e:
    logger.error(f"AI 生成失败: {e}")
    return self._get_enhanced_basic_variants(entity_word)
```

---

### 2. 重试机制
**实现**：使用 tenacity 库，3 次重试，间隔 2 秒

**代码**：
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
    reraise=True
)
async def _call_api(self, prompt: str) -> str:
    # API 调用逻辑
```

---

### 3. 原子操作验证
**实现**：批量删除前验证所有 ID 存在且属于该任务

**代码**：
```python
# 验证所有 ID 是否存在且属于该任务
existing_ids = db.query(SearchTerm.id).filter(
    and_(
        SearchTerm.id.in_(search_term_ids),
        SearchTerm.task_id == task_id,
        SearchTerm.is_deleted == False
    )
).all()

if len(existing_ids) != len(search_term_ids):
    invalid_ids = set(search_term_ids) - set(existing_ids)
    raise ValueError(f"以下ID不存在或不属于该任务: {invalid_ids}")
```

---

### 4. 事务性批量操作
**实现**：使用 SQLAlchemy 的 bulk_save_objects

**代码**：
```python
db_entity_words = [EntityWord(...) for ew in entity_words]
db.bulk_save_objects(db_entity_words)
db.commit()
```

---

### 5. 软删除机制
**实现**：使用 is_deleted 标记，不物理删除

**好处**：
- ✅ 支持恢复操作
- ✅ 保留历史记录
- ✅ 便于审计

---

### 6. 级联软删除
**实现**：删除本体词时，关联的搜索词也被标记为删除

**代码**：
```python
# 4.1 软删除本体词
db.query(EntityWord).filter(...).update({"is_deleted": True})

# 4.2 级联软删除相关的搜索词
db.query(SearchTerm).filter(
    SearchTerm.entity_word_id.in_(deleted_ids)
).update({"is_deleted": True})
```

---

### 7. 分页查询
**实现**：支持 page 和 page_size 参数

**代码**：
```python
offset = (page - 1) * page_size
search_terms = query.order_by(SearchTerm.id.asc()).offset(offset).limit(page_size).all()
```

---

### 8. 搜索词长度验证
**实现**：生成时自动验证长度 ≤ 80 字符

**代码**：
```python
for attr in selected_attributes:
    for ew in selected_entity_words:
        term = f"{attr.word} {ew.entity_word}"
        length = len(term)
        is_valid = length <= max_length
```

---

### 9. 笛卡尔积生成
**实现**：attributes × entity_words 组合

**代码**：
```python
search_terms = []
for attr in selected_attributes:
    for ew in selected_entity_words:
        search_terms.append({
            "term": f"{attr.word} {ew.entity_word}",
            "attribute_id": attr.id,
            "entity_word_id": ew.id,
            "attribute_word": attr.word,
            "entity_word": ew.entity_word,
            "length": len(term),
            "is_valid": len(term) <= 80
        })
```

---

### 10. 按搜索价值星级排序
**实现**：查询时自动按 search_value_stars 降序

**代码**：
```python
query = query.order_by(
    EntityWord.search_value_stars.desc(),
    EntityWord.id.asc()
)
```

---

### 11. 幂等操作
**实现**：重复生成时先删除旧数据

**代码**：
```python
# 检查是否已生成本体词
existing_entity_words = crud_entity_word.get_entity_words_by_task(db, task_id)
if existing_entity_words:
    # 已生成，返回现有数据
    return EntityWordGenerateResponse(...)

# 否则，生成新数据
```

---

### 12. 状态流转
**实现**：任务状态按流程自动更新

**状态流转图**：
```
draft → selected → entity_expanded → entity_selected → combined
```

---

### 13. 自定义词汇支持
**实现**：用户可以添加自定义本体词

**代码**：
```python
if new_entity_words:
    added_count = create_entity_words_batch(
        db, task_id, concept, new_entity_words, source="user"
    )
```

---

### 14. 中英文字段转换
**实现**：AI 返回中文字段，自动转换为英文字段

**代码**：
```python
def convert_entity_word_to_standard(entity_word_data: Dict) -> Dict:
    type_mapping = {
        "原词": "original",
        "同义词": "synonym",
        "变体": "variant"
    }

    return {
        "entity_word": entity_word_data.get("本体词", ""),
        "type": type_mapping.get(entity_word_data.get("词汇类型", "原词"), "original"),
        ...
    }
```

---

### 15. 完整的统计信息
**实现**：每个响应都包含详细的统计信息

**示例**：
```json
{
  "metadata": {
    "total_count": 12,
    "selected_count": 12,
    "type_distribution": {
      "original": 1,
      "synonym": 3,
      "variant": 8
    }
  }
}
```

---

## 测试验证

### 完整测试流程

**测试环境**：Replit
**测试日期**：2025-11-06
**测试结果**：✅ 全部通过

---

### Step 0: 创建任务（Stage 1）

**命令**：
```bash
curl -X POST http://localhost:8001/api/stage1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "waterproof",
    "entity_word": "phone case",
    "max_count": 15
  }'
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "attributes": [...],  // 15 个属性词
  "metadata": {
    "total_count": 15,
    "original_count": 1,
    "synonym_count": 2,
    "related_count": 10,
    "variant_count": 2
  }
}
```

✅ **验证通过**

---

### Step 1: 选择属性词（Stage 2）

**命令**：
```bash
curl -X PUT http://localhost:8001/api/stage2/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/selection \
  -H "Content-Type: application/json" \
  -d '{
    "selected_attribute_ids": [1, 2, 4, 7, 13, 14]
  }'
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "status": "selected",
  "metadata": {
    "selected_count": 6,
    "total_count": 15
  }
}
```

✅ **验证通过**

---

### Step 2: 生成本体词（Stage 3 API 1）

**命令**：
```bash
curl -X POST http://localhost:8001/api/stage3/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/entity-words/generate \
  -H "Content-Type: application/json" \
  -d '{
    "entity_word": "phone case",
    "max_count": 15
  }'
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "entity_words": [
    {"id": 1, "entity_word": "phone case", "type": "original", "search_value_stars": 5},
    {"id": 2, "entity_word": "phone cover", "type": "synonym", "search_value_stars": 5},
    {"id": 3, "entity_word": "phone protector", "type": "synonym", "search_value_stars": 4},
    {"id": 4, "entity_word": "case for phone", "type": "variant", "search_value_stars": 4},
    {"id": 5, "entity_word": "protective phone case", "type": "variant", "search_value_stars": 4},
    {"id": 9, "entity_word": "cell phone case", "type": "variant", "search_value_stars": 4},
    {"id": 6, "entity_word": "phone shell", "type": "synonym", "search_value_stars": 3},
    {"id": 7, "entity_word": "phone cases", "type": "variant", "search_value_stars": 3},
    {"id": 8, "entity_word": "phonecase", "type": "variant", "search_value_stars": 3},
    {"id": 11, "entity_word": "mobile phone case", "type": "variant", "search_value_stars": 3},
    {"id": 10, "entity_word": "phone-case", "type": "variant", "search_value_stars": 2},
    {"id": 12, "entity_word": "case", "type": "variant", "search_value_stars": 2}
  ],
  "metadata": {
    "total_count": 12,
    "selected_count": 12,
    "type_distribution": {
      "original": 1,
      "synonym": 3,
      "variant": 8
    }
  },
  "status": "entity_expanded"
}
```

✅ **验证通过**：AI 成功生成 12 个丰富的本体词

---

### Step 3: 查询本体词（Stage 3 API 2）

**命令**：
```bash
curl http://localhost:8001/api/stage3/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/entity-words
```

**结果**：与 Step 2 相同

✅ **验证通过**

---

### Step 4: 更新本体词选择（Stage 3 API 3）

**命令**：
```bash
curl -X PUT http://localhost:8001/api/stage3/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/entity-words/selection \
  -H "Content-Type: application/json" \
  -d '{
    "selected_entity_word_ids": [1, 2, 3, 4],
    "new_entity_words": [],
    "deleted_entity_word_ids": []
  }'
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "status": "entity_selected",
  "metadata": {
    "selected_count": 4,
    "total_count": 12,
    "changes": {
      "selected": 4,
      "added": 0,
      "deleted": 0
    }
  }
}
```

✅ **验证通过**

---

### Step 5: 生成搜索词（Stage 3 API 4）

**命令**：
```bash
curl -X POST http://localhost:8001/api/stage3/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/search-terms \
  -H "Content-Type: application/json" \
  -d '{
    "options": {
      "max_length": 80
    }
  }'
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "search_terms": [
    // 24 个搜索词（6 属性词 × 4 本体词）
    {"term": "waterproof phone case", "length": 23, "is_valid": true},
    {"term": "waterproof phone cover", "length": 24, "is_valid": true},
    ...
  ],
  "metadata": {
    "total_terms": 24,
    "valid_terms": 24,
    "invalid_terms": 0
  },
  "status": "combined"
}
```

✅ **验证通过**：笛卡尔积正确（6 × 4 = 24）

---

### Step 6: 查询搜索词（Stage 3 API 5）

**命令**：
```bash
curl "http://localhost:8001/api/stage3/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/search-terms?page=1&page_size=20"
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "search_terms": [...],  // 20 个搜索词
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_count": 24,
    "total_pages": 2
  }
}
```

✅ **验证通过**：分页正确

---

### Step 7: 批量删除搜索词（Stage 3 API 6）

**命令**：
```bash
curl -X DELETE http://localhost:8001/api/stage3/tasks/e5598dcc-22b0-4f87-8e5a-7787d1550f6b/search-terms/batch \
  -H "Content-Type: application/json" \
  -d '{
    "search_term_ids": [1, 5, 10]
  }'
```

**结果**：
```json
{
  "task_id": "e5598dcc-22b0-4f87-8e5a-7787d1550f6b",
  "deleted_count": 3,
  "remaining_count": 21,
  "message": "已成功删除 3 个搜索词"
}
```

✅ **验证通过**：原子操作正确（24 - 3 = 21）

---

## 文件清单

### 新增文件

```
app/
├── config/
│   └── prompts/
│       └── entity_word_expert_v1.txt          # 本体词生成 Prompt（512 行）
├── services/
│   └── entity_word_provider.py                # 本体词 AI 服务（369 行）
├── schemas/
│   └── stage3.py                              # Stage 3 API 数据模型（210 行）
├── crud/
│   ├── entity_word.py                         # 本体词 CRUD 操作（216 行）
│   └── search_term.py                         # 搜索词 CRUD 操作（217 行）
└── docs/
    └── stage3_development_summary.md          # 本文档
```

### 修改文件

```
app/
├── main.py                                    # 新增 6 个 API 端点（170+ 行）
├── models_db.py                               # 新增 EntityWord, SearchTerm 模型（60+ 行）
└── database.py                                # 更新表初始化
```

---

## 经验教训

### 1. Prompt 文件花括号问题

**问题**：使用 `.format()` 时，prompt 文件中的 JSON 花括号会被当作变量占位符

**解决方案**：
- 所有 JSON 花括号转义为 `{{` 和 `}}`
- 只有真正的变量保持单花括号：`{entity_word}`

**预防措施**：
- 在代码注释中记录这个问题
- 创建新 prompt 文件时使用模板
- 添加单元测试验证 prompt 格式化

---

### 2. 知识传递的重要性

**问题**：Stage 1 & 2 已经遇到并解决的问题，在 Stage 3 重新犯错

**改进**：
- 记录技术债务和已知问题
- 代码审查时注意相似模式
- 建立 Prompt 文件编写规范

---

### 3. 测试数据缓存问题

**问题**：修改代码后，API 返回的是缓存的旧数据

**解决方案**：
- 清除数据库重新测试
- 或者添加 `force_regenerate` 参数

---

### 4. 调试效率

**问题**：多次来回调试，效率较低

**改进**：
- 先理解问题根本原因
- 再设计解决方案并确认
- 避免盲目尝试修复

---

## 附录

### Git 提交记录

```bash
f948e15 fix(stage3): escape curly braces in prompt template to fix KeyError
48f098d fix(stage3): read API key from environment variable
3ce8ff6 fix(stage3): fix DeepSeekClient import error
9f53cea feat(stage3): implement entity words and search terms functionality
```

### 相关文档

- [Stage 1 & 2 开发文档](./stage1_2_development.md)
- [API 接口文档](./api_documentation.md)
- [数据库设计文档](./database_schema.md)

---

**文档版本**：v1.0
**最后更新**：2025-11-06
**作者**：Claude Code
**状态**：✅ 已完成

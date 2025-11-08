# Replit 环境变量与 Secrets 使用指南

## 📌 重要经验教训

本文档记录了一次生产环境 CORS 配置失败的完整调试过程，揭示了 **Replit Secrets 与 `.env` 文件的关键区别**。

---

## 🔥 问题现象

### 症状
- **本地开发**：一切正常
- **Replit 部署**：CORS 请求返回 `400 Bad Request`
- **错误信息**：`Disallowed CORS origin`

### 困惑点
- Replit Secrets 中明确配置了 `CORS_ALLOWED_ORIGINS`
- Shell 中 `echo $CORS_ALLOWED_ORIGINS` 显示正确
- Python 代码却读取不到，使用了默认值

---

## 🔍 根本原因

### 环境变量加载的两种机制

#### 1. **系统环境变量（Replit Secrets）**
```bash
# 在 Shell 中可见
$ echo $CORS_ALLOWED_ORIGINS
https://example.com,...

# Python 直接读取
import os
os.getenv("CORS_ALLOWED_ORIGINS")  # ✅ 能读取到
```

#### 2. **`.env` 文件（python-dotenv）**
```python
# 需要显式加载
from dotenv import load_dotenv
load_dotenv()  # 从 .env 文件加载变量

import os
os.getenv("CORS_ALLOWED_ORIGINS")  # ⚠️ 只能读取 .env 文件中的值
```

### 关键问题：优先级冲突

当代码中有 `load_dotenv()` 时：

```python
# database.py
from dotenv import load_dotenv
load_dotenv()  # 🚨 这行代码会导致问题！

# main.py
import os
ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "default")
# ❌ 读取的是 .env 文件中的值（如果文件存在）
# ❌ 或者默认值（如果 .env 中没有该变量）
# ❌ 而不是 Replit Secrets！
```

**原因**：`python-dotenv` 的 `load_dotenv()` 会：
1. 读取 `.env` 文件
2. 将文件中的变量加载到环境变量中
3. **但如果 `.env` 文件中没有某个变量，不会去读取系统环境变量（Replit Secrets）**
4. 导致 `os.getenv()` 返回默认值或 `None`

---

## ✅ 正确的做法

### 方案 A：移除 `load_dotenv()`（推荐用于 Replit）

```python
# ❌ 删除或注释掉这些行
# from dotenv import load_dotenv
# load_dotenv()

# ✅ 直接使用 os.getenv()
import os
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "default_value")
```

**优点**：
- 直接读取 Replit Secrets
- 代码更简洁
- 适用于生产环境

**缺点**：
- 本地开发需要手动设置系统环境变量

---

### 方案 B：条件加载（推荐用于多环境）

```python
import os
from dotenv import load_dotenv

# 只在本地开发环境加载 .env 文件
if os.path.exists('.env'):
    load_dotenv()

# 无论如何，os.getenv() 都能正常工作
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "default_value")
```

**优点**：
- 本地开发可以使用 `.env` 文件
- 生产环境（Replit）自动使用 Secrets
- 兼容性最好

**缺点**：
- 需要维护 `.env` 文件（但不提交到 Git）

---

### 方案 C：显式优先级（最安全）

```python
import os
from dotenv import load_dotenv

# 先加载 .env 文件（如果存在）
load_dotenv()

# 然后显式检查系统环境变量
def get_env_var(key, default=None):
    """
    优先读取系统环境变量（Replit Secrets）
    然后才是 .env 文件中的值
    """
    # 先检查是否在系统环境变量中（Replit Secrets）
    import subprocess
    result = subprocess.run(['printenv', key], capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()

    # 如果系统环境变量中没有，再从 os.environ 读取（.env 文件）
    return os.getenv(key, default)

CORS_ALLOWED_ORIGINS = get_env_var("CORS_ALLOWED_ORIGINS", "default_value")
```

**优点**：
- 明确的优先级：Replit Secrets > .env 文件 > 默认值
- 最安全，不会有意外

**缺点**：
- 代码稍微复杂

---

## 🎯 最佳实践

### 1. **开发环境**

创建 `.env` 文件（不提交到 Git）：
```bash
# .env
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
DEEPSEEK_API_KEY=sk-your-dev-key
DATABASE_URL=sqlite:///./dev.db
```

`.gitignore` 中添加：
```
.env
.env.local
.env.*.local
```

### 2. **生产环境（Replit）**

在 Replit Secrets 中配置：
```
Key: CORS_ALLOWED_ORIGINS
Value: https://your-app.vercel.app,https://your-app-preview.vercel.app

Key: DEEPSEEK_API_KEY
Value: sk-your-production-key

Key: DATABASE_URL
Value: postgresql://...
```

### 3. **代码中**

```python
# database.py 或 config.py
import os
from dotenv import load_dotenv

# 条件加载：只在 .env 文件存在时加载
if os.path.exists('.env'):
    load_dotenv()

# 读取环境变量
def get_config(key: str, default: str = None) -> str:
    """
    统一的配置读取函数
    自动处理 Replit Secrets 和 .env 文件
    """
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"环境变量 {key} 未设置")
    return value

# 使用示例
CORS_ALLOWED_ORIGINS = get_config("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
DATABASE_URL = get_config("DATABASE_URL")
API_KEY = get_config("DEEPSEEK_API_KEY")
```

---

## 🐛 调试技巧

### 1. **检查环境变量是否被正确加载**

在代码启动时添加调试日志：

```python
import os

print("=" * 50)
print("环境变量调试信息")
print("=" * 50)

# 检查关键环境变量
env_vars = [
    "CORS_ALLOWED_ORIGINS",
    "DEEPSEEK_API_KEY",
    "DATABASE_URL"
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # 敏感信息只显示前10个字符
        safe_value = value[:10] + "..." if len(value) > 10 else value
        print(f"✅ {var}: {safe_value}")
    else:
        print(f"❌ {var}: 未设置")

print("=" * 50)
```

### 2. **在 Replit Shell 中测试**

```bash
# 检查系统环境变量
echo $CORS_ALLOWED_ORIGINS

# 检查 Python 能否读取
python3 -c "import os; print('Python读取:', os.getenv('CORS_ALLOWED_ORIGINS'))"

# 检查 .env 文件是否存在
ls -la .env

# 如果存在，查看内容
cat .env
```

### 3. **验证 CORS 配置**

```bash
# 测试 CORS 预检请求
curl -X OPTIONS "https://your-replit-app.replit.dev/api/endpoint" \
  -H "Origin: https://your-vercel-app.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

检查响应中是否包含：
```
< Access-Control-Allow-Origin: https://your-vercel-app.vercel.app
< Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
< Access-Control-Allow-Credentials: true
```

---

## 📝 Git 与环境变量

### 哪些文件应该提交到 Git？

| 文件 | 是否提交 | 说明 |
|------|---------|------|
| `.env` | ❌ 否 | 包含敏感信息，每个环境不同 |
| `.env.example` | ✅ 是 | 模板文件，告诉开发者需要哪些变量 |
| `.env.production` | ❌ 否 | 生产环境配置，不应暴露 |
| `config.py` | ✅ 是 | 配置加载逻辑，不包含敏感值 |
| `.gitignore` | ✅ 是 | 必须包含 `.env` 的忽略规则 |

### 创建 `.env.example` 模板

```bash
# .env.example
# 复制此文件为 .env 并填入真实值

# CORS 配置
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# AI 服务配置
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 数据库配置
DATABASE_URL=sqlite:///./bulksheet.db
```

---

## ⚠️ 常见陷阱

### 陷阱 1：认为 Replit Secrets 会自动写入 `.env` 文件
**错误认知**：Replit Secrets 会自动创建 `.env` 文件
**真相**：Replit Secrets 是**系统环境变量**，不会创建文件

### 陷阱 2：认为 `load_dotenv()` 会读取系统环境变量
**错误认知**：`load_dotenv()` 会合并 `.env` 和系统环境变量
**真相**：`load_dotenv()` **只读取 `.env` 文件**，如果文件中没有某个变量，不会从系统环境变量获取

### 陷阱 3：本地能工作，Replit 就能工作
**错误认知**：本地测试通过，生产环境也没问题
**真相**：本地有 `.env` 文件，Replit 没有（因为 `.gitignore` 忽略了）

### 陷阱 4：多次调用 `load_dotenv()` 会覆盖
**错误认知**：多次调用会累加环境变量
**真相**：默认情况下，`load_dotenv()` 不会覆盖已存在的环境变量（除非使用 `override=True`）

---

## 🎓 总结

### 关键要点

1. **Replit Secrets = 系统环境变量**
   - 通过 Replit 界面配置
   - 运行时自动注入到进程中
   - `os.getenv()` 可以直接读取

2. **`.env` 文件 ≠ Replit Secrets**
   - 需要 `python-dotenv` 库加载
   - 被 `.gitignore` 忽略，不会同步到 Git
   - Replit 上不会自动创建

3. **`load_dotenv()` 的局限性**
   - 只加载 `.env` 文件中的变量
   - 如果文件不存在或变量缺失，不会从系统环境变量读取
   - 可能导致 Replit Secrets 被忽略

### 推荐做法

```python
# ✅ 推荐：条件加载
import os
from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv()

CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:5173")
```

### 部署检查清单

- [ ] 确认 Replit Secrets 中所有必需的环境变量已配置
- [ ] 确认 `.env` 文件在 `.gitignore` 中
- [ ] 确认代码能正确处理缺失的 `.env` 文件
- [ ] 在启动日志中添加环境变量加载确认信息
- [ ] 测试 CORS 预检请求返回正确的响应头
- [ ] 验证前端能成功调用后端 API

---

## 📚 参考资料

- [Replit Docs: Secrets](https://docs.replit.com/programming-ide/workspace-features/secrets)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [Environment Variables Best Practices](https://12factor.net/config)

---

## 📅 文档历史

- **2025-11-08**：初始版本，记录 CORS 配置失败的完整调试过程
- **问题背景**：Vercel 前端无法访问 Replit 后端 API
- **根本原因**：`load_dotenv()` 导致 Replit Secrets 未被读取
- **解决方案**：移除或条件化 `load_dotenv()` 调用

---

**作者**：Claude
**项目**：Bulksheet SaaS
**标签**：#replit #环境变量 #cors #部署 #调试经验

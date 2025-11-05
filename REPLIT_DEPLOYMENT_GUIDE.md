# Replit 部署指南

完整的分步部署指南，帮助你将 Bulksheet SaaS 后端部署到 Replit 云平台。

---

## 📋 部署前准备

### 需要上传的文件（7个）

```
backend_v2/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── deepseek_client.py
├── requirements.txt
├── .replit
└── replit.nix
```

### 需要的环境变量

- `DEEPSEEK_API_KEY`: sk-3e26cf2e29d14e4cb26892598336f8ef
- `DEEPSEEK_API_BASE`: https://api.deepseek.com/v1
- `DEEPSEEK_MODEL`: deepseek-chat

---

## 第一步：注册 Replit 账号

### 1.1 访问 Replit
打开浏览器，访问：https://replit.com

### 1.2 使用 GitHub 登录（推荐）
1. 点击右上角 **"Sign up"** 按钮
2. 选择 **"Continue with GitHub"**
3. 授权 Replit 访问你的 GitHub 账号
4. 完成注册（约1分钟）

**优点：**
- 无需额外注册
- 代码自动同步到 GitHub（可选）
- 更安全的身份验证

**或者使用邮箱注册：**
- 点击 "Continue with Email"
- 填写邮箱和密码
- 验证邮箱

---

## 第二步：创建新的 Repl 项目

### 2.1 创建项目
1. 登录后，点击左上角 **"+ Create Repl"** 按钮
2. 在模板选择页面，搜索并选择 **"Python"**
3. 项目配置：
   - **Title**: `bulksheet-saas-backend`（或你喜欢的名字）
   - **Privacy**: 选择 **"Private"**（推荐）
   - **Description**: "AI-powered Amazon Advertising Bulksheet Generator"（可选）
4. 点击 **"+ Create Repl"** 按钮

### 2.2 等待环境初始化
- Replit 会自动创建一个 Python 3.9 环境
- 等待约 10-30 秒，直到看到代码编辑器界面

---

## 第三步：上传项目文件

### 3.1 删除默认文件
Replit 默认会创建一个 `main.py` 文件，我们不需要它：
1. 在左侧文件树中，找到 `main.py`
2. 右键点击 → 选择 **"Delete"**
3. 确认删除

### 3.2 创建 app 目录
1. 点击左侧文件树顶部的 **"+"** 按钮
2. 选择 **"New folder"**
3. 命名为 `app`
4. 按 Enter 确认

### 3.3 上传文件

**方式一：拖拽上传（推荐）**

将本地文件直接拖拽到 Replit 对应位置：

1. **上传到根目录的文件：**
   - 从本地 `backend_v2/` 目录拖拽 `requirements.txt` 到 Replit 根目录
   - 拖拽 `.replit` 到根目录
   - 拖拽 `replit.nix` 到根目录

2. **上传到 app/ 目录的文件：**
   - 从本地 `backend_v2/app/` 目录拖拽以下文件到 Replit 的 `app/` 目录：
     - `__init__.py`
     - `main.py`
     - `models.py`
     - `deepseek_client.py`

**方式二：手动创建文件**

如果拖拽不工作，可以手动创建：

1. 点击对应目录的 **"+"** 按钮
2. 选择 **"New file"**
3. 输入文件名
4. 复制本地文件内容，粘贴到 Replit 编辑器
5. 按 `Ctrl+S` (Windows) 或 `Cmd+S` (Mac) 保存

### 3.4 验证文件结构

上传完成后，你的文件树应该看起来像这样：

```
bulksheet-saas-backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── deepseek_client.py
├── requirements.txt
├── .replit
├── replit.nix
└── .env (稍后创建)
```

---

## 第四步：配置环境变量（Secrets）

### 4.1 打开 Secrets 面板
1. 在左侧工具栏中，找到 🔒 **"Secrets"** 图标（锁形状）
2. 点击打开 Secrets 配置面板

### 4.2 添加环境变量

依次添加以下三个 secrets：

**Secret 1: DEEPSEEK_API_KEY**
- Key: `DEEPSEEK_API_KEY`
- Value: `sk-3e26cf2e29d14e4cb26892598336f8ef`
- 点击 **"Add new secret"**

**Secret 2: DEEPSEEK_API_BASE**
- Key: `DEEPSEEK_API_BASE`
- Value: `https://api.deepseek.com/v1`
- 点击 **"Add new secret"**

**Secret 3: DEEPSEEK_MODEL**
- Key: `DEEPSEEK_MODEL`
- Value: `deepseek-chat`
- 点击 **"Add new secret"**

### 4.3 验证 Secrets
确认你看到了三个绿色的 ✓ 标记，表示 secrets 已成功添加。

**重要提示：**
- Secrets 是加密存储的，只有你能看到
- 不要将 API key 直接写在代码中
- Secrets 会自动注入为环境变量

---

## 第五步：运行应用

### 5.1 点击 Run 按钮
1. 找到编辑器顶部中央的绿色 ▶️ **"Run"** 按钮
2. 点击它

### 5.2 等待安装依赖
第一次运行时，Replit 会自动安装 `requirements.txt` 中的所有依赖。

**控制台输出示例：**
```
> pip install -r requirements.txt
Collecting fastapi==0.121.0
Collecting uvicorn==0.38.0
...
Successfully installed fastapi-0.121.0 uvicorn-0.38.0 ...

> uvicorn app.main:app --host 0.0.0.0 --port 8000
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### 5.3 等待服务器启动
当你看到以下消息时，说明服务器已成功启动：
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**预计时间：**
- 首次运行：2-3 分钟（安装依赖）
- 后续运行：10-20 秒

---

## 第六步：测试 API

### 6.1 获取应用 URL
1. 服务器启动后，Replit 会在右侧显示 **"Webview"** 面板
2. 顶部会显示你的应用 URL，格式类似：
   ```
   https://bulksheet-saas-backend.你的用户名.repl.co
   ```
3. 复制这个 URL（后面测试要用）

### 6.2 测试健康检查端点

**方式一：在 Webview 中测试**
1. Webview 会自动打开根路径 `/`
2. 你应该看到 JSON 响应：
   ```json
   {
     "app": "Bulksheet SaaS",
     "version": "2.0.0",
     "status": "running"
   }
   ```

**方式二：使用 Shell 测试**
1. 在 Replit 左侧工具栏，点击 **"Shell"** 图标
2. 运行命令：
   ```bash
   curl http://localhost:8000/health
   ```
3. 预期输出：
   ```json
   {
     "status": "healthy",
     "message": "API is running"
   }
   ```

### 6.3 测试 Stage 1 API（属性词生成）

**使用 Shell 测试：**

```bash
curl -X POST http://localhost:8000/api/stage1/generate \
  -H "Content-Type: application/json" \
  -d '{"concept": "ocean"}'
```

**预期输出：**
```json
{
  "concept": "ocean",
  "candidates": [
    {
      "word": "ocean",
      "variants": ["oceanic", "sea", "marine", "aquatic"]
    },
    {
      "word": "blue",
      "variants": ["azure", "navy", "cerulean"]
    },
    {
      "word": "wave",
      "variants": ["waves", "surf", "tide"]
    }
  ],
  "task_id": "abc123-def456-..."
}
```

**测试中文输入：**
```bash
curl -X POST http://localhost:8000/api/stage1/generate \
  -H "Content-Type: application/json" \
  -d '{"concept": "海洋"}'
```

### 6.4 使用外部工具测试

**使用 Postman 或 Insomnia：**
1. 创建新的 POST 请求
2. URL: `https://你的应用.repl.co/api/stage1/generate`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "concept": "cute"
   }
   ```
5. 点击 Send

**使用浏览器（前端测试页面）：**
1. 如果你保存了之前的 `test_page.html`
2. 用浏览器打开它
3. 将 Server URL 改为你的 Replit URL
4. 测试各个端点

---

## 第七步：查看日志和调试

### 7.1 查看控制台日志
- **Console 面板**（底部）显示服务器实时日志
- 每个 API 请求都会显示：
  ```
  INFO:     127.0.0.1:12345 - "POST /api/stage1/generate HTTP/1.1" 200 OK
  ```

### 7.2 查看错误信息
如果出现错误，控制台会显示详细的堆栈跟踪：
```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  ...
```

### 7.3 调试技巧

**查看环境变量是否正确：**
1. 在 Shell 中运行：
   ```bash
   python -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"
   ```
2. 应该输出你的 API key（不是 None）

**测试 DeepSeek API 连接：**
```bash
python -c "
import asyncio
from app.deepseek_client import generate_attributes
result = asyncio.run(generate_attributes('test'))
print(result)
"
```

**重启服务器：**
- 点击 Console 面板顶部的 🔄 **"Restart"** 按钮
- 或者点击 ⏹️ **"Stop"** 然后重新点击 ▶️ **"Run"**

---

## 🎉 部署成功标志

如果你看到以下情况，说明部署成功：

✅ **服务器启动成功**
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **健康检查通过**
```bash
curl https://你的应用.repl.co/health
# 返回: {"status": "healthy", "message": "API is running"}
```

✅ **Stage 1 API 工作**
```bash
curl -X POST https://你的应用.repl.co/api/stage1/generate \
  -H "Content-Type: application/json" \
  -d '{"concept": "ocean"}'
# 返回包含 candidates 数组的 JSON
```

---

## ⚠️ 常见问题排查

### 问题 1: 依赖安装失败

**症状：**
```
ERROR: Could not find a version that satisfies the requirement ...
```

**解决方案：**
1. 检查 `requirements.txt` 文件是否正确上传
2. 确认版本号是否正确
3. 尝试在 Shell 中手动安装：
   ```bash
   pip install -r requirements.txt
   ```

### 问题 2: 服务器启动后立即退出

**症状：**
```
INFO:     Started server process
[进程退出]
```

**解决方案：**
1. 检查 `.replit` 文件的 `run` 命令是否正确：
   ```toml
   run = "uvicorn app.main:app --host 0.0.0.0 --port 8000"
   ```
2. 检查 `app/main.py` 语法是否有错误
3. 在 Shell 中运行：
   ```bash
   python -c "import app.main"
   ```
   如果有 import 错误会显示出来

### 问题 3: API 返回 500 错误

**症状：**
```json
{
  "detail": "生成属性词失败: ..."
}
```

**可能原因：**
1. **DeepSeek API Key 无效**
   - 检查 Secrets 中的 `DEEPSEEK_API_KEY` 是否正确
   - 验证 API key 是否过期

2. **网络连接问题**
   - Replit 可能无法访问 DeepSeek API
   - 查看控制台详细错误信息

3. **API 配额用完**
   - 检查 DeepSeek 账户余额

**解决方案：**
- 查看控制台详细错误日志
- 使用 fallback 模式测试（即使 API 失败，应返回规则引擎结果）

### 问题 4: 找不到环境变量

**症状：**
```python
DEEPSEEK_API_KEY = None
```

**解决方案：**
1. 确认 Secrets 已正确添加（左侧 🔒 图标检查）
2. 重启 Repl（Stop + Run）
3. 如果仍然不工作，尝试创建 `.env` 文件：
   ```bash
   # 在 Shell 中运行
   echo "DEEPSEEK_API_KEY=sk-3e26cf2e29d14e4cb26892598336f8ef" > .env
   echo "DEEPSEEK_API_BASE=https://api.deepseek.com/v1" >> .env
   echo "DEEPSEEK_MODEL=deepseek-chat" >> .env
   ```

### 问题 5: CORS 错误（跨域问题）

**症状：**
浏览器控制台显示：
```
Access to fetch at 'https://...' has been blocked by CORS policy
```

**解决方案：**
1. 检查 `app/main.py` 中的 CORS 配置
2. 如果需要允许你的前端域名，更新 `allow_origins`：
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=[
           "http://localhost:3000",
           "https://你的前端域名.com"
       ],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
3. 重启服务器

### 问题 6: Webview 显示空白页

**症状：**
- 右侧 Webview 显示白屏或加载失败

**解决方案：**
1. 检查控制台是否有错误信息
2. 点击 Webview 顶部的 🔄 刷新按钮
3. 点击 Webview 顶部的 🔗 图标，在新标签页打开
4. 使用外部工具（curl, Postman）测试 API 是否真的在运行

---

## 📊 性能和限额

### Replit 免费计划限制

- **始终在线时间**: 应用可能在不活跃后休眠
- **CPU/内存**: 共享资源，高负载时可能变慢
- **网络**: 每月有流量限制

### 激活休眠的应用

如果应用休眠了：
1. 访问你的 Replit URL
2. 等待 10-30 秒自动唤醒
3. 首次请求可能较慢

### 升级建议

如果你需要：
- 24/7 始终在线
- 更快的响应速度
- 更高的流量限额
- 自定义域名

可以升级到 Replit **Hacker Plan**（约 $7/月）

---

## 🔄 更新和迭代

### 如何更新代码

**方式一：直接在 Replit 编辑**
1. 在 Replit 编辑器中修改代码
2. 按 `Ctrl+S` 或 `Cmd+S` 保存
3. 服务器会自动重启（如果使用 `--reload` 模式）

**方式二：重新上传文件**
1. 在本地修改代码
2. 在 Replit 中删除旧文件
3. 拖拽新文件上传
4. 重启服务器

**方式三：Git 同步（进阶）**
1. 在 Replit 中初始化 Git
2. 连接到 GitHub 仓库
3. 本地推送代码后，在 Replit 中 pull

### 回滚到之前版本

Replit 自动保存历史版本：
1. 点击左侧 **"History"** 图标
2. 查看文件修改历史
3. 选择要恢复的版本

---

## 🎯 下一步

部署成功后，你可以：

1. **测试完整功能**
   - 测试各种概念词输入
   - 验证中英文支持
   - 检查错误处理

2. **连接前端**
   - 将前端的 API URL 改为 Replit URL
   - 测试前后端集成

3. **监控和优化**
   - 查看 API 响应时间
   - 优化慢查询
   - 添加日志和监控

4. **添加新功能**
   - Stage 2: 组合生成
   - Stage 3: Bulksheet 导出
   - 用户认证（如需要）

---

## 📚 相关资源

- **Replit 官方文档**: https://docs.replit.com
- **FastAPI 文档**: https://fastapi.tiangolo.com
- **DeepSeek API 文档**: https://platform.deepseek.com/docs
- **项目需求文档**: 查看 `BULKSHEET_REQUIREMENTS.md`

---

## 💬 获取帮助

如果遇到问题：

1. **查看控制台日志** - 90% 的问题都能从日志中找到答案
2. **检查文件结构** - 确保所有文件都在正确位置
3. **验证环境变量** - 确保 Secrets 配置正确
4. **测试基础功能** - 从最简单的 `/health` 端点开始测试
5. **回到 Claude Code** - 将错误信息反馈给我，我会帮你诊断和修复

---

**祝部署顺利！🚀**

如果一切正常，你现在应该有一个运行在云端的 AI 驱动后端 API 了！

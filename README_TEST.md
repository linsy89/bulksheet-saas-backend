# 🎯 快速测试 Stage 1 功能

## 📝 测试步骤（超简单）

### 第 1 步：启动服务器

打开**终端1**，运行：
```bash
cd /Users/linshaoyong/Desktop/bulksheet-saas/backend_v2
bash start_server.sh
```

看到这个就成功了：
```
INFO:     Uvicorn running on http://0.0.0.0:8002
INFO:     Application startup complete.
```

> ⚠️ **保持这个终端窗口打开！** 不要关闭，服务器需要一直运行。

---

### 第 2 步：打开测试网页

**方式 A：双击文件**
- 在Finder中找到 `test_page.html`
- 双击打开

**方式 B：命令行打开**
```bash
open /Users/linshaoyong/Desktop/bulksheet-saas/backend_v2/test_page.html
```

---

### 第 3 步：测试功能

在网页上：

1. **查看状态**
   - 页面顶部应该显示绿色："✅ 后端服务器运行正常"
   - 如果是红色，说明服务器没启动

2. **输入测试**
   - 试试点击示例标签："ocean", "海洋", "cute"
   - 或者自己输入任意概念

3. **生成结果**
   - 点击 "🚀 生成属性词"
   - 等待3-10秒（AI需要时间）
   - 查看生成的属性词和变体

---

## 🎨 预期结果示例

**输入:** `ocean`

**输出:**
```
概念: ocean
任务ID: 550e8400-e29b-41d4-a716-446655440000
生成数量: 5 个属性词

┌─────────────────────┐
│ ocean               │
│ oceanic, sea, marine│
└─────────────────────┘

┌─────────────────────┐
│ beach               │
│ coastal, shore      │
└─────────────────────┘

... (更多属性词)
```

---

## 🔧 其他测试方式

### 方式 1: FastAPI 文档（推荐给开发者）

浏览器打开：
```
http://localhost:8002/docs
```

可以看到完整的API文档和测试界面！

### 方式 2: 命令行测试

打开**终端2**（服务器终端要保持运行），运行：

```bash
# 测试健康检查
curl http://localhost:8002/health

# 测试生成功能
curl -X POST http://localhost:8002/api/stage1/generate \
  -H "Content-Type: application/json" \
  -d '{"concept": "cute"}'
```

---

## ❓ 遇到问题？

### 问题 1: 网页显示红色"无法连接"
**解决：**
1. 确保终端1的服务器在运行
2. 查看终端是否有错误信息
3. 重新运行 `bash start_server.sh`

### 问题 2: 生成很慢或超时
**原因：**
- 正在调用DeepSeek AI（可能需要3-10秒）
- 网络延迟

**解决：**
- 等待最多30秒
- 如果超时，会自动使用备用规则引擎

### 问题 3: 服务器启动失败
**解决：**
```bash
# 停止所有Python进程
pkill -9 python

# 重新启动
bash start_server.sh
```

---

## 📊 技术信息

**服务器地址:** http://localhost:8002

**可用端点:**
- `GET /` - 根端点
- `GET /health` - 健康检查
- `POST /api/stage1/generate` - 生成属性词
- `GET /docs` - API文档

**测试文件:**
- `test_page.html` - 可视化测试页面
- `tests/test_stage1.py` - 自动化测试（pytest）

---

## ✅ 成功标志

如果你看到：
- ✅ 网页显示绿色状态
- ✅ 输入概念后能生成属性词
- ✅ 每个属性词有2-3个变体
- ✅ 响应时间<30秒

**恭喜！Stage 1 功能完全正常！** 🎉

---

## 📸 截图示例

你应该看到类似这样的界面：

```
┌───────────────────────────────────────┐
│ 🎯 Bulksheet SaaS - Stage 1 测试      │
│ 测试属性词生成功能（AI驱动）            │
├───────────────────────────────────────┤
│ ✅ 后端服务器运行正常                   │
├───────────────────────────────────────┤
│ 输入属性概念:                          │
│ [ocean                    ]            │
│ 试试这些: ocean 海洋 cute teen vintage│
│                                        │
│     [🚀 生成属性词]                    │
│                                        │
│ ✨ 生成结果                            │
│ 概念: ocean                            │
│ 任务ID: xxx-xxx-xxx                    │
│ 生成数量: 5 个属性词                    │
│                                        │
│ ┌───────────────┐                     │
│ │ ocean         │                     │
│ │ oceanic sea   │                     │
│ └───────────────┘                     │
└───────────────────────────────────────┘
```

---

**准备好了吗？开始测试吧！** 🚀

# Vercel 部署操作手册

## 📐 代码仓库与部署平台的架构关系

> 💡 **重要提示**：在开始部署前，请先理解整体架构，避免混淆。

### 🏗️ 整体架构图

```
┌─────────────────────────────────────────┐
│          GitHub 仓库（代码中心）          │
│     bulksheet-saas/                     │
│     ├── frontend/      ← 前端代码        │
│     ├── backend_v2/    ← 后端代码        │
│     └── README.md                       │
└──────────────┬──────────────────────────┘
               │
               │ 同一个仓库，两个平台分别使用不同部分
               │
       ┌───────┴────────────────┐
       │                        │
       ▼                        ▼
┌──────────────┐        ┌──────────────┐
│   Vercel     │        │   Replit     │
│  (前端部署)   │        │  (后端运行)   │
├──────────────┤        ├──────────────┤
│ 只使用:       │        │ 只使用:       │
│ frontend/    │        │ backend_v2/  │
│              │        │              │
│ 自动部署 ✅   │        │ 手动同步 🔄   │
└──────────────┘        └──────────────┘
       │                        │
       ▼                        ▼
  前端访问地址              后端API地址
  https://xxx              https://yyy
  .vercel.app              .replit.dev
```

---

### 📂 GitHub 仓库结构说明

#### 1. 单仓库（Monorepo）设计

我们采用**单仓库多项目**的方式：

```bash
bulksheet-saas/                    # GitHub 仓库根目录
│
├── frontend/                      # 前端项目（React + Vite）
│   ├── src/                       # 源代码
│   ├── public/                    # 静态资源
│   ├── package.json               # 前端依赖
│   ├── vite.config.ts            # Vite 配置
│   ├── vercel.json               # Vercel 部署配置
│   └── .env.production           # 生产环境变量
│
├── backend_v2/                    # 后端项目（FastAPI）
│   ├── app/                       # 源代码
│   ├── data/                      # 数据库文件
│   ├── requirements.txt           # Python 依赖
│   └── .replit                   # Replit 运行配置
│
└── README.md                      # 项目说明
```

#### 2. 为什么不分成两个仓库？

**优点**：
- ✅ 前后端版本一致（同一个 commit）
- ✅ API 契约同步更新
- ✅ 管理方便，一次提交更新所有
- ✅ 方便查看完整的项目历史

**缺点**：
- ⚠️ 需要配置平台只使用特定目录

---

### 🟦 Vercel 如何只部署前端？

#### 控制方式：Root Directory 配置

**关键操作**：在 Vercel 配置界面**手动输入**

```
┌─────────────────────────────────────┐
│ Configure Project                    │
├─────────────────────────────────────┤
│ Framework Preset:  [Vite ▼]        │
│                                     │
│ Root Directory:    [frontend  ]  ←─ 👈 必须填写
│                                     │
│ Build Command:     [npm run build] │
│                                     │
│ Output Directory:  [dist        ]  │
└─────────────────────────────────────┘
```

#### 工作原理

1. Vercel 把 `frontend/` 当作项目根目录
2. 在 `frontend/` 目录执行：
   ```bash
   npm install
   npm run build
   ```
3. 部署 `frontend/dist/` 的构建产物

#### 是否需要代码配置？

- ⚠️ **需要手动配置** Root Directory = `frontend`
- ✅ `vercel.json` 是辅助配置（响应头、路由等）
- ❌ 不是完全的代码自动约定

**重要**：如果不填 Root Directory，Vercel 会在项目根目录找 `package.json`，找不到就**部署失败**！

---

### 🟩 Replit 如何只运行后端？

#### 控制方式：.replit 配置文件

**关键文件**：`backend_v2/.replit`

```ini
run = "uvicorn app.main:app --host 0.0.0.0 --port 8000"

modules = ["python-3.9"]

[deployment]
run = ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

#### 工作原理

1. Replit 读取 `.replit` 配置文件
2. 自动执行指定的运行命令
3. 只启动 FastAPI 后端服务

#### 是否需要手动配置？

- ✅ **完全代码约定**，不需要手动配置
- ✅ `.replit` 文件已经在代码仓库中
- ✅ 同步 GitHub 代码时自动同步配置

**优点**：团队成员同步代码后，直接点击 Run 即可，无需额外配置。

---

### 🔄 代码同步工作流

#### 开发阶段

```
本地开发
   │
   ├─ 修改前端代码 (frontend/)
   │  └─ git commit & push
   │     └─ GitHub
   │        └─ Vercel 自动检测 ✅
   │           └─ 自动构建部署 ✅
   │
   └─ 修改后端代码 (backend_v2/)
      └─ git commit & push
         └─ GitHub
            └─ Replit 需要手动 Pull 🔄
               └─ 手动重启服务 🔄
```

#### 前端有改动时

```bash
# 1. 本地修改 frontend/ 代码
# 2. 提交到 GitHub
git add frontend/
git commit -m "feat: update frontend feature"
git push origin main

# 3. Vercel 自动部署 ✅
# 无需任何操作，2-3分钟后自动完成
```

#### 后端有改动时

```bash
# 1. 本地修改 backend_v2/ 代码
cd backend_v2
git add .
git commit -m "feat: update backend API"
git push origin main

# 2. Replit 手动同步 🔄
# 需要在 Replit 网页界面：
#   - 点击 "Version control" → "Pull"
#   - 点击 "Stop" → "Run" 重启服务
```

---

### ❓ 常见疑问 FAQ

#### Q1: GitHub 仓库包含前端+后端，Vercel 会不会把后端代码也部署了？

**A**: ❌ 不会

- Vercel 只看 `Root Directory` 指定的目录（frontend/）
- `backend_v2/` 目录对 Vercel 完全不可见
- Vercel 只会部署 `frontend/dist/` 的静态文件

---

#### Q2: Replit 会不会误运行前端代码？

**A**: ❌ 不会

- `.replit` 文件指定了运行命令：`uvicorn app.main:app`
- 这个命令只启动 FastAPI 后端
- 前端代码不会被执行

---

#### Q3: 为什么 Vercel 能自动部署，Replit 不能？

**A**: 平台特性不同

**Vercel**：
- ✅ 专为前端设计，天生支持 GitHub 自动部署
- ✅ 免费版即支持

**Replit**：
- ⚠️ 免费版需要手动 Pull
- ✅ 付费版可以配置自动同步 GitHub

---

#### Q4: 如果我只改了前端，后端会受影响吗？

**A**: ❌ 不会

- GitHub 是同一个仓库，但部署是独立的
- 改前端：只有 Vercel 重新部署
- 改后端：Replit 不会自动更新（需要手动 Pull）

---

#### Q5: Vercel 和 Replit 的代码是同一份吗？

**A**: ✅ 来源相同，使用不同部分

- **代码来源**：都来自同一个 GitHub 仓库
- **Vercel 使用**：`frontend/` 目录
- **Replit 使用**：`backend_v2/` 目录
- **互不干扰**：各自只关注自己的目录

---

### 📊 对比总结

| 项目 | GitHub | Vercel | Replit |
|------|--------|--------|--------|
| **定位** | 代码中心 | 前端部署 | 后端运行 |
| **使用部分** | 全部代码 | `frontend/` | `backend_v2/` |
| **同步方式** | Git push | 自动检测 ✅ | 手动 Pull 🔄 |
| **配置方式** | - | 网页手动配置 | 代码文件约定 |
| **关键配置** | - | Root Directory | `.replit` 文件 |
| **部署触发** | - | Git push 自动 | 手动重启 |

---

## 📋 部署前准备清单

### ✅ 前端配置已完成
- [x] `vite.config.ts` - 已优化构建配置
- [x] `vercel.json` - 已添加安全响应头
- [x] `.env.production` - 已配置后端地址
- [x] 本地构建测试通过 (`npm run build`)
- [x] TypeScript 类型检查通过

### ✅ 后端配置已完成
- [x] `backend_v2/app/main.py` - CORS 配置已更新
- [x] 删除了 `allow_origins=["*"]` 通配符
- [x] 使用环境变量 `CORS_ALLOWED_ORIGINS`

---

## 📝 部署步骤

### 第一步：部署前端到 Vercel

#### 1.1 访问 Vercel
打开浏览器访问: https://vercel.com

#### 1.2 登录/注册
- 使用 GitHub 账号登录
- 如果没有账号，选择"Sign Up"注册

#### 1.3 创建新项目
1. 点击右上角 "Add New..." 按钮
2. 选择 "Project"
3. 在"Import Git Repository"页面，选择你的 GitHub 仓库
   - 如果看不到仓库，点击"Adjust GitHub App Permissions"授权

#### 1.4 配置项目设置
填写以下配置：

**Project Name**: (自动生成，可自定义)
```
bulksheet-saas
```

**Framework Preset**:
```
Vite
```

**Root Directory**:
```
frontend
```

**Build Command** (默认即可):
```
npm run build
```

**Output Directory** (默认即可):
```
dist
```

#### 1.5 配置环境变量
点击 "Environment Variables" 部分，添加：

| Name | Value | Environment |
|------|-------|-------------|
| `VITE_API_BASE_URL` | `https://3d88dbc8-c986-408e-a27e-754b8acbffb1-00-1m7tsd71rehuu.janeway.replit.dev:8000` | Production, Preview, Development |

**注意**：将上面的 URL 替换为你的实际 Replit 后端地址

#### 1.6 开始部署
1. 点击 "Deploy" 按钮
2. 等待部署完成（大约 2-3 分钟）
3. 部署成功后，记录 Vercel 分配的域名

**示例域名**：
```
https://bulksheet-saas.vercel.app
https://bulksheet-saas-你的用户名.vercel.app
```

---

### 第二步：更新后端 CORS 配置

#### 2.1 登录 Replit
访问: https://replit.com

#### 2.2 打开后端项目
找到并打开你的 Bulksheet SaaS 后端项目

#### 2.3 配置环境变量
1. 点击左侧工具栏的 **🔒 Secrets** 图标（锁形图标）
2. 点击 "+ New Secret"
3. 添加以下环境变量：

**Key**:
```
CORS_ALLOWED_ORIGINS
```

**Value**:
```
http://localhost:5173,http://localhost:5174,https://你的vercel域名.vercel.app
```

**示例**：
```
http://localhost:5173,http://localhost:5174,https://bulksheet-saas.vercel.app
```

**注意**：
- 用你在步骤 1.6 记录的实际 Vercel 域名替换
- 如果 Vercel 给了你多个域名（预览域名、生产域名），都可以添加进去，用逗号分隔
- 保留本地开发地址（localhost:5173 和 localhost:5174）

#### 2.4 重启后端服务
1. 点击顶部的 "Stop" 按钮（如果服务正在运行）
2. 等待服务停止
3. 点击 "Run" 按钮重新启动
4. 确认控制台显示服务启动成功

---

### 第三步：测试部署

#### 3.1 测试前端访问
在浏览器中访问你的 Vercel 域名：
```
https://你的项目名.vercel.app
```

**预期结果**：
- ✅ 页面正常加载
- ✅ 看到"Bulksheet SaaS"标题
- ✅ 四个步骤的向导界面显示正常

#### 3.2 测试 API 连接
进行完整流程测试：

**Step 1: 生成属性词**
1. 输入概念：`waterproof`
2. 输入核心词：`phone case`
3. 点击"生成属性词"
4. **预期**：成功生成属性词列表

**Step 2: 选择属性词**
1. 勾选一些属性词
2. 点击"确认选择"
3. 点击"下一步"
4. **预期**：成功进入 Step 3

**Step 3: 生成本体词**
1. 点击"生成本体词"
2. 勾选一些本体词
3. 点击"确认选择"
4. **预期**：自动生成搜索词
5. 点击"下一步"

**Step 4: 导出 Bulksheet**
1. 填写产品信息：
   - SKU: `TEST-001`
   - ASIN: `B08L5TNJHG`
   - 型号: 选择任意 iPhone 型号
2. 点击"保存产品信息"
3. **预期**：显示绿色确认框
4. 填写预算信息（使用默认值即可）
5. 点击"导出 Bulksheet Excel 文件"
6. **预期**：成功下载 Excel 文件

---

## 🔍 故障排查

### 问题1：前端页面显示空白
**可能原因**：
- 构建失败
- JavaScript 错误

**排查步骤**：
1. 打开浏览器开发者工具（F12）
2. 查看 Console 标签，检查是否有错误信息
3. 查看 Vercel 部署日志：
   - 访问 Vercel 项目页面
   - 点击 "Deployments"
   - 点击最新的部署
   - 查看 "Build Logs"

**解决方案**：
- 如果是构建错误，检查代码是否有语法错误
- 如果是运行时错误，检查环境变量是否配置正确

---

### 问题2：API 请求失败（CORS 错误）
**症状**：
- 浏览器 Console 显示：`Access to fetch at '...' from origin '...' has been blocked by CORS policy`
- Step 1 点击"生成属性词"后无响应或报错

**可能原因**：
- Replit 的 `CORS_ALLOWED_ORIGINS` 未配置
- Replit 的 `CORS_ALLOWED_ORIGINS` 配置错误
- Replit 服务未重启

**排查步骤**：
1. 访问 Replit 项目
2. 检查 Secrets 中的 `CORS_ALLOWED_ORIGINS`
3. 确认值包含你的 Vercel 域名

**解决方案**：
```bash
# 正确的配置示例
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,https://bulksheet-saas.vercel.app

# 如果有多个 Vercel 域名，都添加进去
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,https://bulksheet-saas.vercel.app,https://bulksheet-saas-git-main-username.vercel.app
```

**重要**：修改后必须重启 Replit 后端服务！

---

### 问题3：Replit 后端无响应
**症状**：
- 请求一直 pending
- 超时错误

**可能原因**：
- Replit 后端休眠了（免费版特性）

**解决方案**：
1. 访问 Replit 项目页面
2. 点击 "Run" 按钮唤醒服务
3. 等待 5-10 秒服务启动
4. 重新在前端页面尝试操作

**预防措施**：
- 使用 UptimeRobot 或 cron-job.org 定时 ping 后端
- 升级 Replit 付费版（后端不休眠）

---

### 问题4：环境变量未生效
**症状**：
- API 请求发送到错误的地址
- 控制台显示 `http://localhost:8000` 而不是 Replit 地址

**排查步骤**：
1. 在 Vercel 项目设置中检查环境变量
2. 确认环境变量名称为 `VITE_API_BASE_URL`（注意前缀 `VITE_`）
3. 确认环境变量应用到了正确的环境（Production）

**解决方案**：
1. 访问 Vercel 项目设置
2. 点击 "Settings" → "Environment Variables"
3. 确认 `VITE_API_BASE_URL` 存在且值正确
4. 如果修改了环境变量，需要重新部署：
   - 访问 "Deployments"
   - 点击最新部署右侧的三个点
   - 选择 "Redeploy"

---

## 📊 部署验证清单

### ✅ 前端部署验证
- [ ] Vercel 域名可以正常访问
- [ ] 页面加载正常，无 404 错误
- [ ] 浏览器 Console 无JavaScript 错误
- [ ] 所有页面路由正常（刷新页面不会 404）

### ✅ 后端 CORS 验证
- [ ] Replit Secrets 已配置 `CORS_ALLOWED_ORIGINS`
- [ ] `CORS_ALLOWED_ORIGINS` 包含 Vercel 域名
- [ ] Replit 服务已重启
- [ ] 后端健康检查正常: `/health`

### ✅ 功能测试验证
- [ ] Step 1：可以生成属性词
- [ ] Step 2：可以选择属性词
- [ ] Step 3：可以生成并选择本体词
- [ ] Step 3：可以自动生成搜索词
- [ ] Step 4：可以保存产品信息
- [ ] Step 4：可以成功导出 Excel 文件

### ✅ 性能验证
- [ ] 页面加载时间 < 3 秒
- [ ] API 响应时间 < 2 秒（首次可能 5-10 秒，Replit 唤醒）
- [ ] 构建产物大小合理（< 2MB）

---

## 🎉 部署成功！

如果所有验证都通过，恭喜你！部署成功了！

**你的应用地址**：
- 前端：`https://你的项目名.vercel.app`
- 后端：`https://你的replit地址.replit.dev:8000`
- API 文档：`https://你的replit地址.replit.dev:8000/docs`

---

## 🔄 后续维护

### 代码更新
当你修改代码后：
1. 提交代码到 GitHub
```bash
git add .
git commit -m "描述你的更改"
git push origin main
```
2. Vercel 会自动检测到更新并重新部署
3. 等待 2-3 分钟部署完成

### Replit 后端更新
当修改后端代码后：
1. 在 GitHub 更新代码
2. 在 Replit 项目中：
   - 点击 "Version control" 标签
   - 点击 "Pull" 按钮同步最新代码
   - 点击 "Stop" 然后 "Run" 重启服务

---

## 📞 技术支持

如果遇到问题：
1. 检查本文档的"故障排查"章节
2. 查看 Vercel 部署日志
3. 查看 Replit 控制台日志
4. 查看浏览器开发者工具 Console

常见问题参考：
- Vercel 文档: https://vercel.com/docs
- Replit 文档: https://docs.replit.com

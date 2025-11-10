# 代码同步与维护策略指南

**文档日期**：2025-11-10
**项目**：Bulksheet SaaS
**架构**：GitHub + Vercel (前端) + Replit (后端)
**标签**：#代码维护 #同步策略 #最佳实践

---

## 📋 目录

- [项目架构概览](#项目架构概览)
- [单一事实来源原则](#单一事实来源原则)
- [日常开发流程](#日常开发流程)
- [Replit同步策略](#replit同步策略-重要)
- [Vercel部署策略](#vercel部署策略)
- [常见问题和解决方案](#常见问题和解决方案)
- [快速参考命令](#快速参考命令)
- [部署检查清单](#部署检查清单)

---

## 🏗️ 项目架构概览

### 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         GitHub                               │
│              (唯一的代码权威来源)                              │
│                    main 分支                                  │
└────────────┬────────────────────────────────┬───────────────┘
             │                                │
             │ (自动部署)                      │ (手动同步)
             ↓                                ↓
    ┌────────────────┐              ┌─────────────────┐
    │     Vercel     │              │     Replit      │
    │   (前端部署)    │              │   (后端部署)     │
    │                │              │                 │
    │  frontend/     │              │  backend_v2/    │
    │  React + Vite  │   ←──API──→  │  FastAPI        │
    └────────────────┘              └─────────────────┘
```

### 关键特点

1. **GitHub = 唯一代码源**
   - 所有代码修改必须先推送到GitHub
   - Vercel和Replit都从GitHub获取代码
   - 不在Vercel或Replit上直接修改代码

2. **前后端分离部署**
   - 前端：Vercel自动部署（push到main后自动触发）
   - 后端：Replit手动同步（需要执行git命令）

3. **Monorepo结构**
   ```
   bulksheet-saas/
   ├── frontend/          # Vercel部署这个目录
   ├── backend_v2/        # Replit运行这个目录
   ├── .replit            # Replit配置（必须指向backend_v2）
   ├── REPLIT_*.md        # 部署文档
   └── README.md
   ```

---

## 🎯 单一事实来源原则

### 原则说明

**GitHub是唯一的代码权威来源（Single Source of Truth）**

这意味着：
- ✅ 所有代码修改先在本地完成
- ✅ 测试通过后推送到GitHub
- ✅ Vercel和Replit都从GitHub同步
- ❌ 不在Vercel上修改代码（只读）
- ❌ 不在Replit上直接修改代码（只同步）
- ❌ 不维护多个代码版本

### 为什么这么做？

1. **避免代码不一致**
   - 本地、Vercel、Replit的代码可能不同
   - 导致bug难以复现和修复

2. **简化部署流程**
   - 只需要维护GitHub的代码
   - 部署=同步GitHub代码

3. **方便回滚**
   - Git历史记录了所有变更
   - 可以快速回到任何历史版本

---

## 🔄 日常开发流程

### 标准工作流

```
┌─────────────┐
│ 1. 本地开发  │
│   修改代码   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 2. 本地测试  │
│   验证功能   │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 3. 提交Git  │
│   git commit │
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ 4. 推送GitHub│
│   git push   │
└──────┬──────┘
       │
       ├──────────────┐
       │              │
       ↓              ↓
┌─────────────┐  ┌─────────────┐
│ 5a. Vercel  │  │ 5b. Replit  │
│   自动部署   │  │   手动同步   │
└─────────────┘  └─────────────┘
       │              │
       └──────┬───────┘
              ↓
       ┌─────────────┐
       │ 6. 验证部署  │
       │   E2E测试   │
       └─────────────┘
```

### 详细步骤

#### 1. 本地开发

```bash
# 在本地开发环境（macOS）
cd /Users/linshaoyong/Desktop/bulksheet-saas

# 前端开发
cd frontend
npm run dev  # 启动开发服务器

# 后端开发
cd backend_v2
uvicorn app.main:app --reload  # 启动开发服务器
```

#### 2. 本地测试

```bash
# 前端测试
cd frontend
npm run build  # 确保能正常构建

# 后端测试
cd backend_v2
pytest  # 运行单元测试
python test_full_e2e.py  # 运行E2E测试
```

#### 3. 提交到Git

```bash
# 查看修改
git status
git diff

# 添加文件
git add <files>

# 提交（使用清晰的commit message）
git commit -m "feat: add new feature description"
# 或
git commit -m "fix: resolve issue description"
```

**Commit Message 规范**：
- `feat:` - 新功能
- `fix:` - Bug修复
- `docs:` - 文档更新
- `refactor:` - 代码重构
- `test:` - 测试相关
- `chore:` - 构建/工具相关

#### 4. 推送到GitHub

```bash
git push origin main
```

如果遇到网络超时，增加超时时间：
```bash
git config --global http.postBuffer 524288000
git push origin main
```

#### 5. 部署

**5a. Vercel（自动）**
- Push到GitHub后，Vercel自动检测到变更
- 自动触发构建和部署
- 查看部署日志：https://vercel.com/dashboard
- 通常2-3分钟完成

**5b. Replit（手动）**
- 参见下一节 [Replit同步策略](#replit同步策略-重要)

#### 6. 验证部署

```bash
# 检查前端
curl https://bulksheet-saas-backend.vercel.app

# 检查后端
curl https://你的replit域名/health

# 完整E2E测试
# 在前端页面走一遍Step1-4流程
```

---

## 🔧 Replit同步策略 (重要!)

### 为什么需要特殊策略？

在部署过程中我们遇到了以下问题：

1. **Replit会自动修改 `.replit` 文件**
   - 添加 `[agent]` 配置
   - 添加 `[[ports]]` 配置
   - 产生本地commit

2. **直接 `git pull` 会产生merge冲突**
   ```
   <<<<<<< HEAD
   [agent]
   expertMode = true
   =======
   # GitHub上的版本
   >>>>>>> commit_hash
   ```

3. **冲突标记导致配置文件无法解析**
   ```
   Parse error: unable to decode .replit
   ```

### ✅ 正确的同步方法

**使用 `git reset --hard origin/main` 强制同步**

```bash
# 在Replit Shell执行
cd /home/runner/workspace

# 步骤1：获取最新代码
git fetch origin

# 步骤2：强制用GitHub版本覆盖本地
git reset --hard origin/main

# 步骤3：重启服务
pkill -f uvicorn
# 然后点击Run按钮
```

**输出示例**：
```
HEAD is now at 2ce3f52 debug: add detailed traceback logging for export API errors
```

### ❌ 为什么不用 `git pull`？

```bash
# ❌ 不推荐
git pull origin main

# 可能的结果：
# 1. 提示需要merge策略
hint: You have divergent branches and need to specify how to reconcile them.

# 2. 或者产生merge冲突
CONFLICT (content): Merge conflict in .replit
```

### `git reset --hard` 的优缺点

#### 优点 ✅
- 简单粗暴，不会出错
- 确保代码与GitHub 100%一致
- 避免merge冲突
- 清理所有本地修改

#### 缺点 ⚠️
- 会丢弃本地所有未提交的修改
- 会丢弃Replit的自动commit

#### 为什么缺点不重要？
1. **我们不在Replit上开发代码** - 所以不应该有本地修改
2. **Replit的自动commit不重要** - 只是配置文件的自动修改
3. **单一事实来源原则** - GitHub才是权威

### Replit同步后的验证

同步完成后，检查以下内容：

```bash
# 1. 确认commit是最新的
git log --oneline -1
# 应该显示GitHub上最新的commit hash和message

# 2. 确认.replit配置正确
cat .replit | grep "run ="
# 应该包含: cd backend_v2 && uvicorn...

# 3. 确认代码已更新
head -n 10 backend_v2/app/main.py
# 检查是否是最新的代码
```

### Replit自动修改的处理

同步后，Replit可能又会自动添加 `[agent]` 和 `[[ports]]`：

```bash
$ git status
Changes not staged for commit:
    modified:   .replit
```

**这是正常的！不需要处理！**

原因：
- 这些配置不影响核心功能
- 不需要提交到GitHub
- 下次同步会被覆盖（但Replit会再次添加）

---

## 🚀 Vercel部署策略

### 自动部署流程

Vercel配置了自动部署，流程如下：

```
1. 代码push到GitHub main分支
   ↓
2. Vercel检测到变更（通过Webhook）
   ↓
3. 自动触发构建
   - cd frontend
   - npm install
   - npm run build
   ↓
4. 部署到生产环境
   - 替换旧版本
   - 更新域名指向
   ↓
5. 完成（2-3分钟）
```

### 环境变量更新

如果需要更新环境变量：

1. 登录Vercel Dashboard
2. 选择项目 → Settings → Environment Variables
3. 更新变量值（如 `VITE_API_BASE_URL`）
4. **重要**：点击 "Redeploy" 重新部署

**注意**：只修改环境变量不会自动重新部署，必须手动触发！

### 部署验证

```bash
# 1. 检查部署状态
curl https://bulksheet-saas-backend.vercel.app
# 应该返回HTML（不是404）

# 2. 检查API连接
# 打开浏览器Console，访问前端页面
# 查看Network标签，确认API请求成功

# 3. 完整功能测试
# 手动走一遍Step1-4流程
```

### 回滚策略

如果新版本有问题，Vercel支持一键回滚：

1. Vercel Dashboard → Deployments
2. 找到之前的稳定版本
3. 点击 "···" → "Promote to Production"
4. 确认回滚

或者通过Git回滚：

```bash
# 回退到上一个commit
git revert HEAD
git push origin main
# Vercel会自动部署这个版本
```

---

## 🐛 常见问题和解决方案

### 问题1：Replit运行的是旧代码

**症状**：
- 代码明明已经推送到GitHub
- Replit同步后重启，但还是旧代码
- 添加的调试日志没有出现

**原因**：
- `.replit` 文件指向错误的目录
- 运行的是 `app/` 而不是 `backend_v2/`

**解决方案**：
```bash
# 1. 检查.replit配置
cat .replit | grep "run ="

# 2. 确认包含 cd backend_v2 &&
# 如果没有，说明配置错误

# 3. 强制同步
git fetch origin
git reset --hard origin/main

# 4. 验证进程
ps aux | grep uvicorn
# 应该看到: backend_v2/app.main
```

**参考文档**：[`REPLIT_DEPLOYMENT_CORS_DEBUG.md`](./REPLIT_DEPLOYMENT_CORS_DEBUG.md)

---

### 问题2：环境变量不生效

**症状**：
- Replit Secrets已配置
- Shell里 `echo $VAR` 能看到
- 但Python代码读不到

**原因**：
- 代码里有 `load_dotenv()` 调用
- 覆盖了Replit Secrets

**解决方案**：
```python
# ❌ 删除这些行
from dotenv import load_dotenv
load_dotenv()

# ✅ 直接使用
import os
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS")
```

**参考文档**：[`REPLIT_ENV_SECRETS_GUIDE.md`](./REPLIT_ENV_SECRETS_GUIDE.md)

---

### 问题3：CORS请求失败

**症状**：
- 前端调用后端API返回 `400 Bad Request`
- 错误信息：`Disallowed CORS origin`

**诊断步骤**：
```bash
# 1. 检查服务启动日志
# 应该看到:
🔧 CORS 配置加载
CORS_ALLOWED_ORIGINS 环境变量: https://...
解析后的 ALLOWED_ORIGINS 列表 (共 5 个):
  1. 'https://bulksheet-saas-backend.vercel.app'
  ...

# 2. 测试CORS预检
curl -X OPTIONS "https://你的replit域名/api/stage1/generate" \
  -H "Origin: https://bulksheet-saas-backend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 3. 检查响应头
# 应该包含:
Access-Control-Allow-Origin: https://bulksheet-saas-backend.vercel.app
```

**可能的原因**：
1. 环境变量未配置或错误
2. 运行的是旧代码（没有CORS配置）
3. Vercel URL变化了

**参考文档**：[`REPLIT_DEPLOYMENT_CORS_DEBUG.md`](./REPLIT_DEPLOYMENT_CORS_DEBUG.md)

---

### 问题4：Replit服务未重启

**症状**：
- 代码已同步
- 但行为没有变化

**原因**：
- 代码同步后没有重启uvicorn进程
- 还在运行旧代码

**解决方案**：
```bash
# 方法1：杀死进程
pkill -f uvicorn
# 然后点击Run按钮

# 方法2：点击Replit的Stop按钮，再点击Run

# 验证
ps aux | grep uvicorn
# 检查进程启动时间，应该是刚才重启的时间
```

---

### 问题5：Vercel部署失败

**症状**：
- Push到GitHub后，Vercel显示部署失败
- 或者部署成功但页面空白/404

**诊断步骤**：
1. 查看Vercel部署日志
2. 检查构建命令是否正确
3. 检查环境变量

**常见原因**：
```bash
# 1. 构建命令错误
# Vercel设置 → Build & Development Settings
# Framework Preset: Vite
# Build Command: npm run build (或 cd frontend && npm run build)
# Output Directory: frontend/dist

# 2. Node版本不兼容
# 在package.json添加:
{
  "engines": {
    "node": ">=18.0.0"
  }
}

# 3. 环境变量缺失
# 检查是否配置了 VITE_API_BASE_URL
```

---

## 📚 快速参考命令

### 本地开发

```bash
# 克隆项目
git clone https://github.com/linsy89/bulksheet-saas-backend.git
cd bulksheet-saas

# 前端开发
cd frontend
npm install
npm run dev  # http://localhost:5173

# 后端开发
cd backend_v2
pip install -r requirements.txt
uvicorn app.main:app --reload  # http://localhost:8000

# 运行测试
cd backend_v2
python test_full_e2e.py
```

### Git操作

```bash
# 查看状态
git status
git log --oneline -5

# 提交代码
git add .
git commit -m "feat: description"
git push origin main

# 查看差异
git diff
git diff --cached

# 撤销修改
git restore <file>        # 撤销工作区修改
git restore --staged <file>  # 撤销暂存
git reset --soft HEAD~1   # 撤销最后一次commit（保留修改）
git reset --hard HEAD~1   # 撤销最后一次commit（丢弃修改）
```

### Replit同步（标准流程）

```bash
# === 完整同步流程 ===
cd /home/runner/workspace

# 1. 获取最新代码
git fetch origin

# 2. 强制同步（推荐）
git reset --hard origin/main

# 3. 验证
git log --oneline -1
cat .replit | grep "run ="

# 4. 重启服务
pkill -f uvicorn
# 然后点击Run按钮

# 5. 检查日志
# 查看Console，确认服务启动正常
```

### Replit诊断

```bash
# 检查运行的进程
ps aux | grep uvicorn

# 检查工作目录
lsof -p $(pgrep -f uvicorn) | grep cwd

# 检查环境变量
echo $CORS_ALLOWED_ORIGINS
python3 -c "import os; print(os.getenv('CORS_ALLOWED_ORIGINS'))"

# 检查代码版本
head -n 20 backend_v2/app/main.py

# 测试CORS
curl -X OPTIONS "https://你的replit域名/api/stage1/generate" \
  -H "Origin: https://bulksheet-saas-backend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### Vercel操作

```bash
# 查看部署状态（需要安装vercel CLI）
npm i -g vercel
vercel whoami
vercel ls

# 本地测试Vercel构建
cd frontend
vercel build
vercel dev

# 手动触发部署
vercel --prod
```

---

## ✅ 部署检查清单

### 部署前检查（本地）

- [ ] **代码已测试**
  - [ ] 前端：`npm run build` 成功
  - [ ] 后端：`pytest` 通过
  - [ ] E2E测试通过

- [ ] **Git提交规范**
  - [ ] Commit message清晰
  - [ ] 没有包含敏感信息（密钥、密码）
  - [ ] `.gitignore` 正确配置

- [ ] **环境变量**
  - [ ] 文档记录了新增的环境变量
  - [ ] `.env.example` 已更新

- [ ] **文档更新**
  - [ ] README更新（如有新功能）
  - [ ] API文档更新（如有新接口）

### 推送到GitHub

- [ ] **推送成功**
  ```bash
  git push origin main
  # 看到: To https://github.com/...
  #       xxx..xxx  main -> main
  ```

- [ ] **GitHub上确认**
  - [ ] 访问GitHub仓库，确认最新commit
  - [ ] 检查文件内容正确

### Vercel部署验证

- [ ] **自动部署触发**
  - [ ] Vercel Dashboard显示 "Building"
  - [ ] 等待2-3分钟

- [ ] **部署成功**
  - [ ] 状态变为 "Ready"
  - [ ] 没有构建错误

- [ ] **功能验证**
  - [ ] 访问 https://bulksheet-saas-backend.vercel.app
  - [ ] 页面正常加载
  - [ ] 打开Console，无错误

### Replit部署验证

- [ ] **代码同步**
  ```bash
  cd /home/runner/workspace
  git fetch origin
  git reset --hard origin/main
  ```

- [ ] **验证同步**
  ```bash
  git log --oneline -1  # 确认是最新commit
  cat .replit | grep "run ="  # 确认配置正确
  ```

- [ ] **重启服务**
  ```bash
  pkill -f uvicorn
  # 点击Run按钮
  ```

- [ ] **检查日志**
  - [ ] 看到 "🔧 CORS 配置加载"
  - [ ] 看到 "✅ AI 服务已初始化"
  - [ ] 看到 "✅ 数据库表初始化完成"
  - [ ] 没有错误信息

- [ ] **测试API**
  ```bash
  curl https://你的replit域名/health
  # 应该返回: {"status":"healthy",...}
  ```

### E2E功能验证

- [ ] **完整流程测试**
  - [ ] Step1: 输入概念和核心词 → 生成属性词
  - [ ] Step2: 选择属性词 → 保存
  - [ ] Step3: 生成本体词 → 生成搜索词
  - [ ] Step4: 填写产品信息 → 导出Excel

- [ ] **CORS验证**
  - [ ] 前端能正常调用后端API
  - [ ] Network标签显示200 OK
  - [ ] 没有CORS错误

- [ ] **导出功能**
  - [ ] Excel文件成功下载
  - [ ] 文件可以正常打开
  - [ ] 数据完整且格式正确

### 问题排查

如果出现问题，按以下顺序检查：

1. **前端问题**
   - [ ] 检查Vercel部署日志
   - [ ] 检查浏览器Console错误
   - [ ] 检查Network请求状态

2. **后端问题**
   - [ ] 检查Replit Console日志
   - [ ] 检查进程是否正确：`ps aux | grep uvicorn`
   - [ ] 检查环境变量：`echo $CORS_ALLOWED_ORIGINS`

3. **CORS问题**
   - [ ] 参考 [`REPLIT_DEPLOYMENT_CORS_DEBUG.md`](./REPLIT_DEPLOYMENT_CORS_DEBUG.md)
   - [ ] 测试CORS预检请求
   - [ ] 检查Replit Secrets配置

4. **回滚**
   - [ ] Vercel: Dashboard → Deployments → 选择稳定版本 → Promote
   - [ ] Replit: `git reset --hard <stable_commit_hash>`

---

## 🎓 最佳实践总结

### DO（应该做的）✅

1. **始终从GitHub同步代码**
   - 本地 → GitHub → Vercel/Replit
   - 保持单一事实来源

2. **使用 `git reset --hard` 同步Replit**
   - 简单可靠，不会出错
   - 避免merge冲突

3. **每次部署后验证**
   - 检查日志
   - 测试关键功能
   - 确认CORS正常

4. **记录环境变量变更**
   - 更新 `.env.example`
   - 文档记录用途

5. **清晰的Commit Message**
   - 使用约定式提交（Conventional Commits）
   - 便于追溯历史

### DON'T（不应该做的）❌

1. **不在Replit上直接修改代码**
   - 修改会在下次同步时丢失
   - 导致代码不一致

2. **不使用 `git pull` 同步Replit**
   - 容易产生merge冲突
   - 冲突标记导致配置文件损坏

3. **不忘记重启服务**
   - 代码同步后必须重启
   - 否则还是运行旧代码

4. **不在Vercel上手动修改环境变量后不重新部署**
   - 环境变量修改不会自动生效
   - 必须触发Redeploy

5. **不提交敏感信息到Git**
   - API密钥、密码等放在Replit Secrets
   - 使用 `.gitignore` 忽略 `.env` 文件

---

## 📞 故障响应流程

### 级别1：功能异常（非紧急）

**症状**：某个功能不工作，但系统整体可用

**响应步骤**：
1. 查看Replit Console日志，定位错误
2. 检查相关代码提交历史
3. 本地复现问题
4. 修复并测试
5. 推送到GitHub
6. 同步到Replit并验证

**预计时间**：30分钟 - 2小时

---

### 级别2：服务不可用（紧急）

**症状**：整个服务挂了，用户无法访问

**响应步骤**：

1. **立即回滚到稳定版本**（5分钟内）
   ```bash
   # Vercel回滚
   # Dashboard → Deployments → 选择稳定版本 → Promote

   # Replit回滚
   cd /home/runner/workspace
   git log --oneline -10  # 找到稳定版本commit hash
   git reset --hard <stable_commit>
   pkill -f uvicorn  # 重启
   ```

2. **验证服务恢复**
   - 测试前端访问
   - 测试后端API
   - 通知用户服务已恢复

3. **分析根本原因**
   - 查看日志
   - 对比代码差异
   - 找出导致问题的commit

4. **修复并重新部署**
   - 本地修复问题
   - 充分测试
   - 推送并部署

**预计时间**：回滚5分钟，修复1-4小时

---

## 📝 变更日志

| 日期 | 变更内容 | 原因 |
|------|---------|------|
| 2025-11-10 | 初始版本 | 总结部署经验，建立维护策略 |
| - | - | - |

---

## 📚 相关文档

- [`REPLIT_DEPLOYMENT_CORS_DEBUG.md`](./REPLIT_DEPLOYMENT_CORS_DEBUG.md) - CORS调试经验（3小时问题排查）
- [`REPLIT_ENV_SECRETS_GUIDE.md`](./REPLIT_ENV_SECRETS_GUIDE.md) - Replit Secrets与.env文件的区别
- [`DEPLOYMENT_CONFIG_FINAL.md`](./DEPLOYMENT_CONFIG_FINAL.md) - 部署配置清单

---

## 🎯 下次更新计划

- [ ] 添加自动化脚本（一键同步Replit）
- [ ] 添加监控告警机制
- [ ] 添加性能指标追踪
- [ ] 建立灾难恢复流程

---

**作者**：Claude
**项目**：Bulksheet SaaS
**维护者**：开发团队

**如有问题或改进建议，请在GitHub创建Issue！**

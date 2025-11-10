# Vercel + Replit 部署最终配置方案

## 📋 配置变更总览

本文档包含所有需要修改的配置文件的**最终版本**，请仔细审核后再执行。

> **📚 相关文档**：
> - [`REPLIT_DEPLOYMENT_CORS_DEBUG.md`](./REPLIT_DEPLOYMENT_CORS_DEBUG.md) - **CORS持续失败的调试经验**（必读！记录了3小时调试过程和解决方案）
> - [`REPLIT_ENV_SECRETS_GUIDE.md`](./REPLIT_ENV_SECRETS_GUIDE.md) - Replit Secrets与.env文件的区别

---

## 1. 后端 CORS 配置修改（关键安全配置）

### 文件：`backend_v2/app/main.py`

**当前配置（第111-117行）**：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发阶段：允许所有来源 ⚠️ 不安全
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**修改为（生产环境安全配置）**：
```python
import os

# CORS配置 - 生产环境：仅允许指定域名
# 从环境变量读取允许的源，默认为本地开发
ALLOWED_ORIGINS = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # ✅ 仅允许指定域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # ✅ 明确指定方法
    allow_headers=["Content-Type", "Authorization"],  # ✅ 明确指定头部
)
```

**需要在 Replit Secrets 中添加环境变量**：
```
Key: CORS_ALLOWED_ORIGINS
Value: http://localhost:5173,http://localhost:5174,https://你的项目名.vercel.app
```

**说明**：
- ❌ 删除了 `["*"]` 通配符（安全风险）
- ✅ 使用环境变量动态配置允许的域名
- ✅ 限制了 HTTP 方法和请求头
- ✅ 支持本地开发 + Vercel 生产环境
- 🔧 部署到 Vercel 后，将实际的 Vercel 域名添加到环境变量中

---

## 2. 前端 Vite 配置优化

### 文件：`frontend/vite.config.ts`

**完整配置**：
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],

  // 路径别名配置
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // 构建优化配置
  build: {
    // 输出目录
    outDir: 'dist',
    // 生成 sourcemap 用于生产环境调试
    sourcemap: false,
    // 代码分割策略
    rollupOptions: {
      output: {
        manualChunks: {
          // React 相关库单独打包
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          // Ant Design 单独打包
          'antd-vendor': ['antd', '@ant-design/icons'],
        },
      },
    },
    // chunk 大小警告限制
    chunkSizeWarningLimit: 1000,
  },

  // 开发服务器配置
  server: {
    port: 5173,
    // 开发环境代理配置（可选）
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

---

## 3. Vercel 配置文件

### 文件：`frontend/vercel.json`

**完整配置**：
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",

  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],

  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        {
          "key": "X-Content-Type-Options",
          "value": "nosniff"
        },
        {
          "key": "X-Frame-Options",
          "value": "DENY"
        },
        {
          "key": "X-XSS-Protection",
          "value": "1; mode=block"
        },
        {
          "key": "Referrer-Policy",
          "value": "strict-origin-when-cross-origin"
        }
      ]
    }
  ],

  "env": {
    "VITE_API_BASE_URL": "@vite_api_base_url"
  }
}
```

---

## 4. 前端环境变量配置

### 文件：`frontend/.env.production`

**内容**：
```bash
# 生产环境配置
# 注意：这个文件会被提交到 Git，不要包含敏感信息

# Replit 后端地址（请替换为你的实际地址）
VITE_API_BASE_URL=https://3d88dbc8-c986-408e-a27e-754b8acbffb1-00-1m7tsd71rehuu.janeway.replit.dev:8000
```

### Vercel 环境变量（在 Vercel 控制台配置）

需要在 Vercel 项目设置中添加：

```
Name: VITE_API_BASE_URL
Value: https://你的replit地址.replit.dev:8000
Environment: Production, Preview, Development
```

---

## 5. API 客户端优化（可选）

### 文件：`frontend/src/api/client.ts`

**如果需要添加超时和重试逻辑**：

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000, // 30秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证 token 等
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 统一错误处理
    if (error.response) {
      // 服务器返回错误
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // 请求发出但没有收到响应（网络错误、超时等）
      console.error('Network Error:', error.message);
    } else {
      // 其他错误
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export { apiClient };

// 导出通用请求方法
export const api = {
  get: <T = any>(url: string, config?: any) =>
    apiClient.get<T>(url, config).then(res => res.data),

  post: <T = any, D = any>(url: string, data?: D, config?: any) =>
    apiClient.post<T>(url, data, config).then(res => res.data),

  put: <T = any, D = any>(url: string, data?: D, config?: any) =>
    apiClient.put<T>(url, data, config).then(res => res.data),

  delete: <T = any>(url: string, config?: any) =>
    apiClient.delete<T>(url, config).then(res => res.data),
};
```

---

## 6. 部署清单（29项检查）

### 前端准备
- [ ] 1. 更新 `vite.config.ts` 配置
- [ ] 2. 确认 `vercel.json` 配置正确
- [ ] 3. 创建 `.env.production` 文件
- [ ] 4. 确认 `.gitignore` 包含 `.env.local`（但不包含 `.env.production`）
- [ ] 5. 本地运行 `npm run build` 测试构建
- [ ] 6. 本地运行 `npm run preview` 测试生产版本
- [ ] 7. 检查构建产物大小（dist 目录）
- [ ] 8. 提交所有前端代码到 GitHub

### 后端准备
- [ ] 9. 修改 `backend_v2/app/main.py` CORS 配置
- [ ] 10. 在 Replit Secrets 添加 `CORS_ALLOWED_ORIGINS` 环境变量
- [ ] 11. 在 Replit 重启后端服务
- [ ] 12. 测试后端健康检查：`GET /health`
- [ ] 13. 提交后端代码到 GitHub
- [ ] 14. 同步 GitHub 到 Replit

### Vercel 部署
- [ ] 15. 注册/登录 Vercel 账号
- [ ] 16. 在 Vercel 点击 "New Project"
- [ ] 17. 导入 GitHub 仓库
- [ ] 18. 设置 Root Directory 为 `frontend`
- [ ] 19. 设置 Framework Preset 为 `Vite`
- [ ] 20. 添加环境变量 `VITE_API_BASE_URL`
- [ ] 21. 点击 "Deploy" 开始部署
- [ ] 22. 等待部署完成（约2-3分钟）
- [ ] 23. 记录 Vercel 分配的域名

### 集成测试
- [ ] 24. 更新后端 Replit 的 `CORS_ALLOWED_ORIGINS`（添加 Vercel 域名）
- [ ] 25. 在 Replit 重启后端服务
- [ ] 26. 访问 Vercel 域名，测试前端加载
- [ ] 27. 测试 Step 1：生成属性词
- [ ] 28. 测试完整流程：Step 1 → 2 → 3 → 4
- [ ] 29. 测试 Excel 文件导出

---

## 7. 环境变量汇总

### Replit 后端环境变量

在 Replit Secrets（左侧工具栏 🔒 图标）中配置：

```bash
# 开发+生产环境
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:5174,https://你的项目名.vercel.app

# DeepSeek API（如果还没有）
DEEPSEEK_API_KEY=your_api_key_here
```

### Vercel 前端环境变量

在 Vercel 项目设置 → Environment Variables 中配置：

```bash
VITE_API_BASE_URL=https://你的replit地址.replit.dev:8000
```

---

## 8. 部署后的 URL

部署成功后，你将得到：

```
前端: https://你的项目名.vercel.app
后端: https://你的replit地址.replit.dev:8000
API 文档: https://你的replit地址.replit.dev:8000/docs
```

---

## 9. 故障排查

### 问题1：前端加载空白页
**检查**：
- 浏览器控制台是否有 JavaScript 错误
- Vercel 部署日志是否有构建错误
- `dist/index.html` 是否正确生成

### 问题2：API 请求失败（CORS 错误）
**检查**：
- Replit 的 `CORS_ALLOWED_ORIGINS` 是否包含 Vercel 域名
- Replit 服务是否正在运行
- 浏览器控制台具体的 CORS 错误信息

**解决方案**：
```bash
# 在 Replit Secrets 中确认配置
CORS_ALLOWED_ORIGINS=https://你的项目名.vercel.app,https://你的项目名-git-main-你的用户名.vercel.app
```

### 问题3：Replit 后端休眠
**现象**：首次访问等待5-10秒

**解决方案**：
1. 免费方案：接受首次访问的等待时间
2. 付费方案：升级 Replit 保持常驻运行
3. 自动唤醒：使用 cron-job.org 每 25 分钟 ping 一次后端

---

## 10. 成本和性能

### 当前方案（Vercel + Replit）

**成本**：¥0/月
**性能**：
- 前端：全球 CDN，访问速度快
- 后端：首次访问可能需要 5-10 秒唤醒

### 升级路径（需要时）

**方案A**：Replit 付费版
- 成本：约 $7/月
- 优势：后端常驻运行，无休眠

**方案B**：云服务器
- 成本：约 ¥60-100/月
- 优势：完全控制，更高性能

---

## 11. 下一步建议

### 功能增强
- [ ] 添加用户认证（登录/注册）
- [ ] 添加任务历史记录
- [ ] 添加导出历史查看
- [ ] 添加数据统计看板

### 性能优化
- [ ] 添加 API 缓存
- [ ] 添加 Loading 状态优化
- [ ] 添加错误边界处理
- [ ] 添加 PWA 支持

### 监控和运维
- [ ] 配置 Sentry 错误监控
- [ ] 配置 Google Analytics
- [ ] 配置 UptimeRobot 服务监控

---

## ✅ 确认事项

在执行部署前，请确认：

1. **CORS 配置**：
   - ✅ 已删除 `["*"]` 通配符
   - ✅ 使用环境变量动态配置域名
   - ✅ 限制了 HTTP 方法和头部

2. **环境变量**：
   - ✅ Replit 配置了 `CORS_ALLOWED_ORIGINS`
   - ✅ Vercel 配置了 `VITE_API_BASE_URL`

3. **构建测试**：
   - ✅ 本地 `npm run build` 成功
   - ✅ 本地 `npm run preview` 可以访问

4. **代码提交**：
   - ✅ 所有更改已提交到 GitHub
   - ✅ Replit 已同步最新代码

---

**请仔细审核以上所有配置，确认无误后告诉我可以开始执行！**

# Bulksheet SaaS - 前端项目

AI 驱动的亚马逊广告关键词生成工具前端。

## 技术栈

- React 18
- TypeScript
- Vite
- React Router 6
- TanStack Query
- Ant Design 5
- Tailwind CSS
- Axios

## 开发环境设置

### 1. 安装依赖

```bash
npm install
```

### 2. 配置环境变量

编辑 `.env` 文件，设置后端 API 地址：

```env
VITE_API_BASE_URL=你的Replit后端URL
```

### 3. 启动开发服务器

```bash
npm run dev
```

浏览器会自动打开 `http://localhost:5173`

## 项目结构

```
frontend/
├── src/
│   ├── api/                 # API 客户端
│   ├── components/          # 组件
│   ├── pages/               # 页面
│   ├── types/               # TypeScript 类型
│   └── router.tsx           # 路由配置
├── .env                     # 环境变量
└── package.json
```

## 构建生产版本

```bash
npm run build
```

#!/bin/bash

# Bulksheet SaaS Backend 启动脚本

echo "🚀 启动 Bulksheet SaaS 后端服务器..."
echo ""

# 切换到backend_v2目录
cd /Users/linshaoyong/Desktop/bulksheet-saas/backend_v2

# 激活虚拟环境
source venv/bin/activate

# 停止现有进程（改进版）
echo "📋 停止现有服务器进程..."
pkill -9 -f "uvicorn app.main:app" 2>/dev/null

# 清理8002端口
echo "🔧 清理端口 8002..."
lsof -ti :8002 | xargs kill -9 2>/dev/null

sleep 2

# 启动服务器
echo "✨ 启动新服务器 (http://localhost:8002)..."
echo "📖 API文档: http://localhost:8002/docs"
echo "🧪 测试页面: 打开 test_page.html"
echo ""
echo "⚠️  按 Ctrl+C 停止服务器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 只监控 app 目录的变化，避免监控 venv 导致频繁重启
uvicorn app.main:app --reload --reload-dir app --host 0.0.0.0 --port 8002

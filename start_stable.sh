#!/bin/bash

# 稳定模式启动脚本（不使用reload）

echo "🚀 启动 Bulksheet SaaS 后端服务器（稳定模式）..."
echo ""

cd /Users/linshaoyong/Desktop/bulksheet-saas/backend_v2

source venv/bin/activate

# 停止现有进程
echo "📋 停止现有服务器进程..."
pkill -9 -f "uvicorn" 2>/dev/null
lsof -ti :8002 | xargs kill -9 2>/dev/null

sleep 2

# 启动服务器（稳定模式，不监控文件变化）
echo "✨ 启动新服务器 (http://localhost:8002)..."
echo "📖 API文档: http://localhost:8002/docs"
echo "🧪 测试页面: 打开 test_page.html"
echo ""
echo "⚠️  按 Ctrl+C 停止服务器"
echo "⚠️  注意：稳定模式下修改代码不会自动重启"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 不使用 --reload，更稳定
uvicorn app.main:app --host 0.0.0.0 --port 8002

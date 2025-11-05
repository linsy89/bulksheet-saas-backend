"""
最简单的测试 - 检查基本导入
"""

print("1. 测试基本导入...")
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI导入成功")
except Exception as e:
    print(f"   ❌ FastAPI导入失败: {e}")
    exit(1)

print("2. 测试创建应用...")
try:
    app = FastAPI()
    print("   ✅ FastAPI应用创建成功")
except Exception as e:
    print(f"   ❌ 创建应用失败: {e}")
    exit(1)

print("3. 测试导入models...")
try:
    from app import models
    print("   ✅ models模块导入成功")
except Exception as e:
    print(f"   ❌ models导入失败: {e}")
    exit(1)

print("4. 测试导入deepseek_client...")
try:
    from app import deepseek_client
    print("   ✅ deepseek_client模块导入成功")
except Exception as e:
    print(f"   ❌ deepseek_client导入失败: {e}")
    print(f"   错误详情: {e}")
    exit(1)

print("5. 测试导入main...")
try:
    from app import main
    print("   ✅ main模块导入成功")
except Exception as e:
    print(f"   ❌ main导入失败: {e}")
    exit(1)

print("\n🎉 所有测试通过！")
print("\n现在可以尝试启动服务器了。")

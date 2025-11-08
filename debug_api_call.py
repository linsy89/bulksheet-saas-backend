#!/usr/bin/env python3
"""调试API调用问题"""

from playwright.sync_api import sync_playwright
import time

def debug_api_call():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # 收集控制台日志
        console_logs = []
        page.on("console", lambda msg: console_logs.append(f"[{msg.type}] {msg.text}"))

        # 收集网络错误
        network_errors = []
        page.on("response", lambda response:
            network_errors.append(f"❌ {response.status} {response.url}")
            if response.status >= 400 else None
        )

        print("📍 1. 访问向导页面...")
        page.goto('http://localhost:5174/wizard')
        page.wait_for_load_state('networkidle')

        print("📍 2. 填写表单...")
        page.fill('input[placeholder*="cute"]', 'cute')
        page.fill('input[placeholder*="phone case"]', 'phone case')

        print("📍 3. 提交表单...")
        page.click('button:has-text("生成属性词")')

        # 等待10秒看看发生了什么
        print("⏳ 等待10秒观察...")
        time.sleep(10)

        # 截图
        page.screenshot(path='/tmp/debug_after_submit.png', full_page=True)

        print("\n📋 控制台日志:")
        for log in console_logs[-20:]:  # 显示最后20条
            print(f"   {log}")

        print("\n🌐 网络错误:")
        for error in network_errors:
            print(f"   {error}")

        # 检查是否有错误消息显示
        error_msg = page.locator('.ant-message-error').count()
        if error_msg > 0:
            print(f"\n❌ 页面显示错误消息: {page.locator('.ant-message-error').inner_text()}")

        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    debug_api_call()

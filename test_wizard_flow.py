#!/usr/bin/env python3
"""测试向导流程：从步骤1到步骤2"""

from playwright.sync_api import sync_playwright
import time

def test_wizard_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # 使用可见模式方便调试
        page = browser.new_page()

        print("📍 1. 访问首页...")
        page.goto('http://localhost:5174')
        page.wait_for_load_state('networkidle')
        page.screenshot(path='/tmp/step0_homepage.png')

        print("📍 2. 点击'开始创建'按钮...")
        page.click('text=开始创建')
        page.wait_for_load_state('networkidle')
        page.screenshot(path='/tmp/step1_form.png')

        print("📍 3. 填写表单...")
        # 填写产品属性概念
        page.fill('input[placeholder*="cute"]', 'cute')

        # 填写产品核心词
        page.fill('input[placeholder*="phone case"]', 'phone case')

        page.screenshot(path='/tmp/step1_filled.png')

        print("📍 4. 提交表单并等待AI生成（预计30-60秒）...")
        page.click('button:has-text("生成属性词")')

        # 等待加载动画出现
        page.wait_for_selector('text=AI 正在生成属性词', timeout=5000)
        print("⏳ AI生成中，请耐心等待...")

        # 等待成功消息（最多120秒）
        page.wait_for_selector('text=成功生成', timeout=120000)
        print("✅ AI生成完成！")

        # 等待自动跳转到步骤2
        time.sleep(2)
        page.wait_for_load_state('networkidle')
        page.screenshot(path='/tmp/step2_table.png', full_page=True)

        print("📍 5. 验证步骤2内容...")
        # 检查是否显示了表格
        table_exists = page.locator('table').count() > 0
        print(f"   - 表格是否存在: {table_exists}")

        # 检查是否有属性词数据
        rows = page.locator('tbody tr').count()
        print(f"   - 属性词数量: {rows}")

        # 检查右侧信息卡片
        concept_text = page.locator('text=产品概念').count() > 0
        print(f"   - 右侧信息卡片显示: {concept_text}")

        print("\n📍 6. 测试表格交互...")
        if rows > 0:
            # 选择前3个属性词
            checkboxes = page.locator('tbody input[type="checkbox"]')
            for i in range(min(3, rows)):
                checkboxes.nth(i).check()

            page.screenshot(path='/tmp/step2_selected.png', full_page=True)
            print(f"   - 已选择 3 个属性词")

            # 检查选择计数
            selected_text = page.locator('text=/已选择.*个属性词/').inner_text()
            print(f"   - 选择状态: {selected_text}")

        print("\n✅ 测试完成！截图已保存到 /tmp/")
        print("   - step0_homepage.png: 首页")
        print("   - step1_form.png: 步骤1表单")
        print("   - step1_filled.png: 填写后的表单")
        print("   - step2_table.png: 步骤2表格")
        print("   - step2_selected.png: 选中属性词后")

        # 保持浏览器打开5秒供查看
        time.sleep(5)
        browser.close()

if __name__ == '__main__':
    test_wizard_flow()

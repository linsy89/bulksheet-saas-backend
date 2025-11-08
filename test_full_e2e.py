#!/usr/bin/env python3
"""
端到端完整流程测试脚本 - 包含 Step 4 测试
测试完整的四步流程：生成属性词 → 选择属性词 → 生成并选择本体词 → 生成搜索词 → 保存产品信息 → 导出
"""

import requests
import json
from datetime import datetime
import os

BASE_URL = "https://3d88dbc8-c986-408e-a27e-754b8acbffb1-00-1m7tsd71rehuu.janeway.replit.dev:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_success(msg):
    print(f"✅ {msg}")

def print_error(msg):
    print(f"❌ {msg}")

def print_info(msg):
    print(f"ℹ️  {msg}")

def test_stage1_generate():
    """测试 Stage 1: 生成属性词"""
    print_section("📝 Stage 1: 生成属性词")

    url = f"{BASE_URL}/api/stage1/generate"
    payload = {
        "concept": "waterproof",
        "entity_word": "phone case"
    }

    print(f"POST {url}")
    print(f"请求体: {json.dumps(payload, indent=2)}")

    response = requests.post(url, json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        return None, None

    data = response.json()
    task_id = data.get("task_id")
    attributes = data.get("attributes", [])

    print_success(f"成功生成 {len(attributes)} 个属性词")
    print_info(f"Task ID: {task_id}")

    # 检查ID字段
    attrs_with_id = [attr for attr in attributes if 'id' in attr and attr['id'] is not None]
    print_info(f"所有属性词都包含数据库ID: {len(attrs_with_id)}/{len(attributes)}")

    if len(attrs_with_id) < len(attributes):
        print_error(f"警告: {len(attributes) - len(attrs_with_id)} 个属性词缺少ID!")
        return None, None

    # 显示前3个属性词
    print("\n前3个属性词:")
    for i, attr in enumerate(attributes[:3], 1):
        print(f"  {i}. [{attr['id']}] {attr['word']} ({attr['type']}) - {attr['translation']}")

    return task_id, attributes

def test_stage2_selection(task_id, attributes):
    """测试 Stage 2: 选择属性词"""
    print_section("🎯 Stage 2: 选择属性词")

    # 选择前10个属性词
    selected_ids = [attr['id'] for attr in attributes[:10]]

    url = f"{BASE_URL}/api/stage2/tasks/{task_id}/selection"
    payload = {
        "selected_attribute_ids": selected_ids,
        "new_attributes": [],
        "deleted_attribute_ids": []
    }

    print(f"PUT {url}")
    print(f"选择的属性词ID: {selected_ids}")

    response = requests.put(url, json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        return False

    data = response.json()
    selected_count = data.get('metadata', {}).get('selected_count', 0)

    print_success(f"成功选择 {selected_count} 个属性词")

    if selected_count != len(selected_ids):
        print_error(f"期望选中 {len(selected_ids)} 个，但API返回 {selected_count} 个")
        return False

    return True

def test_stage3_generate_entity_words(task_id):
    """测试 Stage 3.1: 生成本体词"""
    print_section("🔧 Stage 3.1: 生成本体词")

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/entity-words/generate"

    print(f"POST {url}")
    response = requests.post(url, json={})

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        return None

    data = response.json()
    entity_words = data.get("entity_words", [])

    print_success(f"成功生成 {len(entity_words)} 个本体词")

    # 显示前5个本体词
    print("\n前5个本体词:")
    for i, ew in enumerate(entity_words[:5], 1):
        print(f"  {i}. [{ew['id']}] {ew['entity_word']} ({ew['type']}) - {ew.get('translation', 'N/A')}")

    return entity_words

def test_stage3_select_entity_words(task_id, entity_words):
    """测试 Stage 3.2: 选择本体词"""
    print_section("🎯 Stage 3.2: 选择本体词")

    # 选择前6个本体词
    selected_ids = [ew['id'] for ew in entity_words[:6]]

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/entity-words/selection"
    payload = {
        "selected_entity_word_ids": selected_ids,
        "new_entity_words": [],
        "deleted_entity_word_ids": []
    }

    print(f"PUT {url}")
    print(f"选择的本体词ID: {selected_ids}")

    response = requests.put(url, json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        return False

    data = response.json()
    selected_count = data.get('metadata', {}).get('selected_count', 0)

    print_success(f"成功选择 {selected_count} 个本体词")

    if selected_count != len(selected_ids):
        print_error(f"期望选中 {len(selected_ids)} 个，但API返回 {selected_count} 个")
        return False

    return True

def test_stage3_generate_search_terms(task_id):
    """测试 Stage 3.3: 生成搜索词"""
    print_section("🔍 Stage 3.3: 生成搜索词")

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/search-terms"

    print(f"POST {url}")
    response = requests.post(url, json={})

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        try:
            error_data = response.json()
            print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            pass
        return None

    data = response.json()
    search_terms = data.get("search_terms", [])
    metadata = data.get("metadata", {})

    print_success(f"成功生成 {len(search_terms)} 个搜索词!")
    print_info(f"组合: {metadata.get('attribute_count')} 属性词 × {metadata.get('entity_word_count')} 本体词")

    # 显示前5个搜索词
    print("\n前5个搜索词:")
    for i, st in enumerate(search_terms[:5], 1):
        print(f"  {i}. [{st['id']}] {st['term']}")

    return search_terms

def test_stage4_save_product_info(task_id):
    """测试 Stage 4.1: 保存产品信息"""
    print_section("📦 Stage 4.1: 保存产品信息")

    url = f"{BASE_URL}/api/stage4/save-product-info"
    payload = {
        "task_id": task_id,
        "sku": "TEST-SKU-001",
        "asin": "B08L5TNJHG",
        "model": "iPhone 16 Pro Max"
    }

    print(f"POST {url}")
    print(f"请求体: {json.dumps(payload, indent=2)}")

    response = requests.post(url, json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        return False

    data = response.json()
    print_success(f"产品信息保存成功!")
    print_info(f"SKU: {payload['sku']}")
    print_info(f"ASIN: {payload['asin']}")
    print_info(f"型号: {payload['model']}")

    return True

def test_stage4_export(task_id):
    """测试 Stage 4.2: 导出 Bulksheet"""
    print_section("📥 Stage 4.2: 导出 Bulksheet")

    url = f"{BASE_URL}/api/stage4/export"
    payload = {
        "task_id": task_id,
        "daily_budget": 1.5,
        "ad_group_default_bid": 0.45,
        "keyword_bid": 0.45
    }

    print(f"POST {url}")
    print(f"请求体: {json.dumps(payload, indent=2)}")

    response = requests.post(url, json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print_error(f"失败: {response.text}")
        return False

    # 检查返回的是否是 Excel 文件
    content_type = response.headers.get('Content-Type', '')
    content_length = len(response.content)

    print_success(f"Bulksheet 导出成功!")
    print_info(f"Content-Type: {content_type}")
    print_info(f"文件大小: {content_length} bytes ({content_length / 1024:.2f} KB)")

    # 保存文件
    filename = f"bulksheet_{task_id}_{int(datetime.now().timestamp())}.xlsx"
    filepath = os.path.join("/tmp", filename)

    with open(filepath, 'wb') as f:
        f.write(response.content)

    print_success(f"文件已保存到: {filepath}")

    # 验证文件是否为有效的 Excel 文件（检查文件头）
    if response.content[:4] == b'PK\x03\x04':  # ZIP 文件头（Excel 是 ZIP 格式）
        print_success("文件格式验证: 有效的 Excel 文件 (xlsx)")
    else:
        print_error("文件格式验证: 不是有效的 Excel 文件")
        return False

    return True

def main():
    print("\n" + "🧪"*40)
    print("  端到端完整流程测试 (E2E)")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🧪"*40)

    # Stage 1: 生成属性词
    task_id, attributes = test_stage1_generate()
    if not task_id:
        print_error("Stage 1 失败，测试终止")
        return

    # Stage 2: 选择属性词
    stage2_ok = test_stage2_selection(task_id, attributes)
    if not stage2_ok:
        print_error("Stage 2 失败，测试终止")
        return

    # Stage 3.1: 生成本体词
    entity_words = test_stage3_generate_entity_words(task_id)
    if not entity_words:
        print_error("Stage 3.1 失败，测试终止")
        return

    # Stage 3.2: 选择本体词
    stage3_2_ok = test_stage3_select_entity_words(task_id, entity_words)
    if not stage3_2_ok:
        print_error("Stage 3.2 失败，测试终止")
        return

    # Stage 3.3: 生成搜索词
    search_terms = test_stage3_generate_search_terms(task_id)
    if not search_terms:
        print_error("Stage 3.3 失败，测试终止")
        return

    # Stage 4.1: 保存产品信息
    stage4_1_ok = test_stage4_save_product_info(task_id)
    if not stage4_1_ok:
        print_error("Stage 4.1 失败，测试终止")
        return

    # Stage 4.2: 导出 Bulksheet
    stage4_2_ok = test_stage4_export(task_id)
    if not stage4_2_ok:
        print_error("Stage 4.2 失败，测试终止")
        return

    # 测试总结
    print_section("📊 测试总结")
    print_success("所有测试通过! 🎉")
    print(f"\n完整流程验证成功:")
    print(f"  ✅ Stage 1: 生成属性词")
    print(f"  ✅ Stage 2: 选择属性词")
    print(f"  ✅ Stage 3.1: 生成本体词")
    print(f"  ✅ Stage 3.2: 选择本体词")
    print(f"  ✅ Stage 3.3: 生成搜索词")
    print(f"  ✅ Stage 4.1: 保存产品信息")
    print(f"  ✅ Stage 4.2: 导出 Bulksheet")

    print(f"\n📋 任务信息:")
    print(f"  Task ID: {task_id}")
    print(f"  属性词: {len(attributes)} 个 (选择了 10 个)")
    print(f"  本体词: {len(entity_words)} 个 (选择了 6 个)")
    print(f"  搜索词: {len(search_terms)} 个 (10 × 6 = 60)")
    print(f"  预算设置: 每日 $1.5, 广告组/关键词出价 $0.45")

    print("\n✨ 四步向导流程完整验证成功！\n")

if __name__ == "__main__":
    main()

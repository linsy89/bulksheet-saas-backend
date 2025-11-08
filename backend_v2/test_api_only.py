#!/usr/bin/env python3
"""
API 测试脚本 - 诊断属性词ID问题（仅测试API，不检查数据库）
"""

import requests
import json
from datetime import datetime

BASE_URL = "https://3d88dbc8-c986-408e-a27e-754b8acbffb1-00-1m7tsd71rehuu.janeway.replit.dev:8000"

def print_section(title):
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def test_stage1_generate():
    """测试 Stage 1: 生成属性词 - 重点检查是否有ID"""
    print_section("🔍 Stage 1: 生成属性词（检查ID）")

    url = f"{BASE_URL}/api/stage1/generate"
    payload = {
        "concept": "waterproof",
        "entity_word": "phone case"
    }

    print(f"POST {url}")
    response = requests.post(url, json=payload)

    print(f"状态码: {response.status_code}\n")

    if response.status_code != 200:
        print(f"❌ 失败: {response.text}")
        return None, None

    data = response.json()
    task_id = data.get("task_id")
    attributes = data.get("attributes", [])

    print(f"✅ 成功生成 {len(attributes)} 个属性词")
    print(f"Task ID: {task_id}\n")

    # 关键检查：前3个属性词的完整结构
    print("📋 前3个属性词的完整JSON结构:")
    print("-" * 80)
    for i, attr in enumerate(attributes[:3], 1):
        print(f"\n属性词 #{i}:")
        print(json.dumps(attr, indent=2, ensure_ascii=False))

    # 检查ID字段
    print("\n" + "-" * 80)
    print("🔍 ID字段检查:")
    attrs_with_id = [attr for attr in attributes if 'id' in attr and attr['id'] is not None]
    attrs_without_id = [attr for attr in attributes if 'id' not in attr or attr['id'] is None]

    print(f"  ✅ 有ID的属性词: {len(attrs_with_id)} 个")
    print(f"  ❌ 没ID的属性词: {len(attrs_without_id)} 个")

    if attrs_with_id:
        ids = [attr['id'] for attr in attrs_with_id[:5]]
        print(f"  示例ID: {ids}")

    if attrs_without_id:
        print(f"  ⚠️  警告: {len(attrs_without_id)} 个属性词缺少ID字段！")
        print(f"  这会导致前端使用合成ID，从而引发 Stage 2 更新失败")

    return task_id, attributes

def test_stage2_selection(task_id, attributes):
    """测试 Stage 2: 选择属性词"""
    print_section("🔍 Stage 2: 选择属性词（使用实际ID）")

    # 决定使用真实ID还是合成ID
    if attributes and attributes[0].get('id') is not None:
        selected_ids = [attr['id'] for attr in attributes[:10] if 'id' in attr]
        print(f"✅ 使用真实的数据库ID: {selected_ids}")
    else:
        selected_ids = list(range(1, 11))
        print(f"⚠️  使用合成ID (模拟前端行为): {selected_ids}")
        print(f"    这可能导致更新失败，因为数据库中没有这些ID!")

    url = f"{BASE_URL}/api/stage2/tasks/{task_id}/selection"
    payload = {
        "selected_attribute_ids": selected_ids,
        "new_attributes": [],
        "deleted_attribute_ids": []
    }

    print(f"\nPUT {url}")
    print(f"请求体: {json.dumps(payload, indent=2)}")

    response = requests.put(url, json=payload)
    print(f"\n状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ 失败!")
        print(f"错误响应: {response.text}")
        return False

    data = response.json()
    selected_count = data.get('metadata', {}).get('selected_count', 0)

    print(f"✅ API 成功响应!")
    print(f"   selected_count: {selected_count}")

    if selected_count != len(selected_ids):
        print(f"\n⚠️  警告: 期望选中 {len(selected_ids)} 个，但API返回 {selected_count} 个")
        print(f"    这表明有些ID在数据库中不存在!")
        return False

    return True

def test_stage3_generate_entity_words(task_id):
    """测试 Stage 3: 生成本体词"""
    print_section("🔍 Stage 3.1: 生成本体词")

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/entity-words/generate"
    response = requests.post(url, json={})

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ 失败: {response.text}")
        return None

    data = response.json()
    entity_words = data.get("entity_words", [])
    print(f"✅ 成功生成 {len(entity_words)} 个本体词")

    return entity_words

def test_stage3_select_entity_words(task_id, entity_words):
    """测试 Stage 3: 选择本体词"""
    print_section("🔍 Stage 3.2: 选择本体词")

    selected_ids = [ew['id'] for ew in entity_words[:6]]

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/entity-words/selection"
    payload = {
        "selected_entity_word_ids": selected_ids,
        "new_entity_words": [],
        "deleted_entity_word_ids": []
    }

    print(f"选择的本体词ID: {selected_ids}")
    response = requests.put(url, json=payload)

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ 失败: {response.text}")
        return False

    data = response.json()
    print(f"✅ 成功选择 {data.get('metadata', {}).get('selected_count')} 个本体词")
    return True

def test_stage3_generate_search_terms(task_id):
    """测试 Stage 3: 生成搜索词 - 可能失败的地方"""
    print_section("🔍 Stage 3.3: 生成搜索词（关键测试）")

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/search-terms"
    response = requests.post(url, json={})

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"\n❌ 失败! 这就是问题所在!")
        try:
            error_data = response.json()
            print(f"错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"错误文本: {response.text}")

        print("\n🔍 问题诊断:")
        print("  根据错误'没有选中的属性词'，说明:")
        print("  1. Stage 2 的属性词选择API虽然返回200，但实际没有更新数据库")
        print("  2. 最可能的原因: Stage 1 返回的属性词没有真实的数据库ID")
        print("  3. 前端使用了合成ID (1,2,3...)，但数据库中的真实ID可能是 (567,568,569...)")
        print("  4. 导致 Stage 2 更新时找不到对应的记录")

        return False

    data = response.json()
    search_terms = data.get("search_terms", [])
    metadata = data.get("metadata", {})

    print(f"✅ 成功生成 {len(search_terms)} 个搜索词!")
    print(f"   组合: {metadata.get('attribute_count')} × {metadata.get('entity_word_count')}")

    return True

def main():
    print("\n" + "🧪"*40)
    print("  API 诊断测试 - 聚焦属性词ID问题")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🧪"*40)

    # Stage 1 - 关键检查点
    task_id, attributes = test_stage1_generate()
    if not task_id:
        return

    # Stage 2
    stage2_ok = test_stage2_selection(task_id, attributes)

    # Stage 3
    entity_words = test_stage3_generate_entity_words(task_id)
    if not entity_words:
        return

    test_stage3_select_entity_words(task_id, entity_words)

    # Stage 3.3 - 最终测试
    search_terms_ok = test_stage3_generate_search_terms(task_id)

    # 总结
    print_section("📊 测试总结")

    if search_terms_ok:
        print("✅ 所有测试通过!")
    else:
        print("❌ 搜索词生成失败")
        print("\n根本原因分析:")

        if attributes and attributes[0].get('id') is None:
            print("  🎯 确认: Stage 1 API 返回的属性词 **没有** 数据库ID")
            print("     - 前端只能使用合成ID (1,2,3...)")
            print("     - Stage 2 使用这些假ID更新数据库时，找不到对应记录")
            print("     - 导致 is_selected 字段没有被更新")
            print("     - Stage 3 查询时找不到选中的属性词")
            print("\n  💡 解决方案:")
            print("     需要修改后端 Stage 1 API，返回带有数据库ID的属性词")
        elif not stage2_ok:
            print("  🎯 Stage 2 API返回的selected_count与预期不符")
            print("     - 说明有些ID在数据库中不存在")
            print("\n  💡 解决方案:")
            print("     检查数据库实际存储的ID范围")

    print(f"\nTask ID: {task_id}")
    print("可以在 Replit 数据库中查看这个任务的详细数据\n")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
完整流程测试脚本 - 诊断属性词选择问题

测试流程：
1. Stage 1: 生成属性词
2. 检查返回的属性词是否包含数据库ID
3. Stage 2: 选择属性词
4. 验证数据库中的 is_selected 状态
5. Stage 3: 生成本体词
6. Stage 3: 选择本体词
7. Stage 3: 生成搜索词（这里可能会失败）
"""

import requests
import json
import sqlite3
from datetime import datetime

BASE_URL = "https://3d88dbc8-c986-408e-a27e-754b8acbffb1-00-1m7tsd71rehuu.janeway.replit.dev:8000"

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def check_database_attributes(task_id):
    """检查数据库中的属性词状态"""
    print_section("📊 检查数据库中的属性词状态")

    conn = sqlite3.connect('bulksheet.db')
    cursor = conn.cursor()

    # 查询所有属性词
    cursor.execute("""
        SELECT id, word, is_selected, is_deleted
        FROM task_attributes
        WHERE task_id = ?
        ORDER BY id
    """, (task_id,))

    rows = cursor.fetchall()

    print(f"数据库中共有 {len(rows)} 个属性词：\n")

    selected_count = 0
    for row in rows:
        attr_id, word, is_selected, is_deleted = row
        status = "✅ 已选中" if is_selected else "⬜ 未选中"
        deleted = " [已删除]" if is_deleted else ""
        print(f"  ID={attr_id:3d}  {status}  {word:30s}{deleted}")
        if is_selected and not is_deleted:
            selected_count += 1

    print(f"\n总计: 已选中 {selected_count} 个属性词")

    conn.close()
    return selected_count

def test_stage1_generate():
    """测试 Stage 1: 生成属性词"""
    print_section("🚀 Stage 1: 生成属性词")

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
        print(f"❌ 请求失败: {response.text}")
        return None, None

    data = response.json()
    task_id = data.get("task_id")
    attributes = data.get("attributes", [])

    print(f"✅ 成功生成 {len(attributes)} 个属性词")
    print(f"   Task ID: {task_id}")

    # 检查前3个属性词的结构
    print(f"\n📋 前3个属性词的数据结构:")
    for i, attr in enumerate(attributes[:3]):
        print(f"\n属性词 #{i+1}:")
        print(f"  - word: {attr.get('word')}")
        print(f"  - id: {attr.get('id')} {'✅' if 'id' in attr else '❌ 缺少id字段！'}")
        print(f"  - type: {attr.get('type')}")
        print(f"  - is_selected: {attr.get('is_selected')}")

    # 检查所有属性词是否都有 id
    attrs_without_id = [attr for attr in attributes if 'id' not in attr]
    if attrs_without_id:
        print(f"\n⚠️  警告: 有 {len(attrs_without_id)} 个属性词没有 id 字段！")
    else:
        print(f"\n✅ 所有属性词都包含 id 字段")

    return task_id, attributes

def test_stage2_selection(task_id, attributes):
    """测试 Stage 2: 选择属性词"""
    print_section("🚀 Stage 2: 选择属性词")

    # 提取前10个属性词的ID（或者使用合成的ID）
    if attributes[0].get('id') is not None:
        # 使用真实ID
        selected_ids = [attr['id'] for attr in attributes[:10] if 'id' in attr]
        print(f"使用真实的数据库ID: {selected_ids}")
    else:
        # 使用合成ID（模拟前端行为）
        selected_ids = list(range(1, 11))
        print(f"⚠️  属性词没有ID，使用合成ID: {selected_ids}")

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
        print(f"❌ 请求失败: {response.text}")
        return False

    data = response.json()
    print(f"✅ 成功!")
    print(f"   selected_count: {data.get('metadata', {}).get('selected_count', 0)}")
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")

    # 验证数据库
    db_selected_count = check_database_attributes(task_id)

    api_selected_count = data.get('metadata', {}).get('selected_count', 0)

    if db_selected_count == api_selected_count and db_selected_count == len(selected_ids):
        print(f"\n✅ 数据一致性检查通过:")
        print(f"   API返回: {api_selected_count} 个")
        print(f"   数据库: {db_selected_count} 个")
        print(f"   预期: {len(selected_ids)} 个")
        return True
    else:
        print(f"\n❌ 数据一致性检查失败:")
        print(f"   API返回: {api_selected_count} 个")
        print(f"   数据库: {db_selected_count} 个")
        print(f"   预期: {len(selected_ids)} 个")
        return False

def test_stage3_generate_entity_words(task_id):
    """测试 Stage 3: 生成本体词"""
    print_section("🚀 Stage 3.1: 生成本体词")

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/entity-words/generate"
    payload = {}

    print(f"POST {url}")

    response = requests.post(url, json=payload)

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ 请求失败: {response.text}")
        return None

    data = response.json()
    entity_words = data.get("entity_words", [])

    print(f"✅ 成功生成 {len(entity_words)} 个本体词")

    return entity_words

def test_stage3_select_entity_words(task_id, entity_words):
    """测试 Stage 3: 选择本体词"""
    print_section("🚀 Stage 3.2: 选择本体词")

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

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"❌ 请求失败: {response.text}")
        return False

    data = response.json()
    print(f"✅ 成功选择 {data.get('metadata', {}).get('selected_count')} 个本体词")

    return True

def test_stage3_generate_search_terms(task_id):
    """测试 Stage 3: 生成搜索词（可能会失败的地方）"""
    print_section("🚀 Stage 3.3: 生成搜索词（关键测试点）")

    url = f"{BASE_URL}/api/stage3/tasks/{task_id}/search-terms"
    payload = {}

    print(f"POST {url}")

    response = requests.post(url, json=payload)

    print(f"状态码: {response.status_code}")

    if response.status_code != 200:
        print(f"\n❌ 请求失败！")
        print(f"错误信息: {response.text}")

        # 再次检查数据库状态
        print("\n🔍 再次检查数据库中的属性词状态:")
        check_database_attributes(task_id)

        return False

    data = response.json()
    search_terms = data.get("search_terms", [])
    metadata = data.get("metadata", {})

    print(f"✅ 成功生成 {len(search_terms)} 个搜索词!")
    print(f"   组合方式: {metadata.get('attribute_count')} 属性词 × {metadata.get('entity_word_count')} 本体词")

    return True

def main():
    """主测试流程"""
    print("\n" + "🧪"*40)
    print("  完整流程诊断测试")
    print("  测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("🧪"*40)

    # Stage 1
    task_id, attributes = test_stage1_generate()
    if not task_id:
        print("\n❌ Stage 1 失败，测试终止")
        return

    # Stage 2
    success = test_stage2_selection(task_id, attributes)
    if not success:
        print("\n❌ Stage 2 数据不一致，继续测试看看会发生什么...")

    # Stage 3.1
    entity_words = test_stage3_generate_entity_words(task_id)
    if not entity_words:
        print("\n❌ Stage 3.1 失败，测试终止")
        return

    # Stage 3.2
    success = test_stage3_select_entity_words(task_id, entity_words)
    if not success:
        print("\n❌ Stage 3.2 失败，测试终止")
        return

    # Stage 3.3 - 关键测试点
    success = test_stage3_generate_search_terms(task_id)

    print_section("📊 测试总结")
    if success:
        print("✅ 所有测试通过！搜索词生成成功！")
    else:
        print("❌ 搜索词生成失败 - 这就是我们要找的bug")
        print("\n可能的原因:")
        print("1. Stage 1 API 返回的属性词没有包含数据库ID")
        print("2. 前端使用了合成ID，导致 Stage 2 更新失败")
        print("3. 数据库中实际没有被标记为 is_selected=True 的属性词")

    print(f"\nTask ID: {task_id}")
    print("可以用这个 task_id 在数据库中进一步调查\n")

if __name__ == "__main__":
    main()

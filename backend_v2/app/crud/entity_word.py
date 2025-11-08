"""
EntityWord CRUD 操作
本体词的数据库增删改查
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, delete
from typing import List, Dict, Tuple
from app.models_db import EntityWord, SearchTerm


def create_entity_words_batch(db: Session, task_id: str, concept: str, entity_words: List[Dict], source: str = "ai") -> int:
    """
    批量创建本体词

    Args:
        db: 数据库会话
        task_id: 任务ID
        concept: 原始属性概念
        entity_words: 本体词列表
        source: 来源（ai/user）

    Returns:
        创建的数量
    """
    db_entity_words = []

    for ew in entity_words:
        db_entity_word = EntityWord(
            task_id=task_id,
            entity_word=ew["entity_word"],
            concept=concept,
            type=ew["type"],
            translation=ew.get("translation"),
            use_case=ew.get("use_case"),
            search_value=ew["search_value"],
            search_value_stars=ew["search_value_stars"],
            recommended=ew["recommended"],
            source=source,
            is_selected=True,  # 默认全部选中
            is_deleted=False
        )
        db_entity_words.append(db_entity_word)

    db.bulk_save_objects(db_entity_words)
    db.commit()

    return len(db_entity_words)


def get_entity_words_by_task(db: Session, task_id: str, include_deleted: bool = False) -> List[EntityWord]:
    """
    查询任务的本体词列表

    Args:
        db: 数据库会话
        task_id: 任务ID
        include_deleted: 是否包含已删除的本体词

    Returns:
        本体词列表
    """
    query = db.query(EntityWord).filter(EntityWord.task_id == task_id)

    if not include_deleted:
        query = query.filter(EntityWord.is_deleted == False)

    # 按搜索价值星级降序、ID 升序排序
    query = query.order_by(EntityWord.search_value_stars.desc(), EntityWord.id.asc())

    return query.all()


def update_entity_word_selection(
    db: Session,
    task_id: str,
    selected_ids: List[int],
    new_entity_words: List[Dict],
    deleted_ids: List[int],
    concept: str
) -> Tuple[int, int, int]:
    """
    更新本体词选中状态

    Args:
        db: 数据库会话
        task_id: 任务ID
        selected_ids: 选中的本体词ID列表
        new_entity_words: 新增的自定义本体词
        deleted_ids: 要删除的本体词ID列表
        concept: 原始属性概念

    Returns:
        (selected_count, added_count, deleted_count)
    """
    # 1. 将该任务所有本体词设置为未选中
    db.query(EntityWord).filter(
        and_(
            EntityWord.task_id == task_id,
            EntityWord.is_deleted == False
        )
    ).update({"is_selected": False}, synchronize_session=False)

    # 2. 将指定ID设置为选中
    if selected_ids:
        db.query(EntityWord).filter(
            and_(
                EntityWord.id.in_(selected_ids),
                EntityWord.task_id == task_id,
                EntityWord.is_deleted == False
            )
        ).update({"is_selected": True}, synchronize_session=False)

    # 3. 添加自定义本体词
    added_count = 0
    if new_entity_words:
        added_count = create_entity_words_batch(db, task_id, concept, new_entity_words, source="user")

    # 4. 软删除本体词（级联）
    deleted_count = 0
    if deleted_ids:
        # 4.1 软删除本体词
        db.query(EntityWord).filter(
            and_(
                EntityWord.id.in_(deleted_ids),
                EntityWord.task_id == task_id
            )
        ).update({"is_deleted": True, "is_selected": False}, synchronize_session=False)

        # 4.2 级联软删除相关的搜索词
        db.query(SearchTerm).filter(
            and_(
                SearchTerm.entity_word_id.in_(deleted_ids),
                SearchTerm.task_id == task_id
            )
        ).update({"is_deleted": True}, synchronize_session=False)

        deleted_count = len(deleted_ids)

    db.commit()

    # 5. 统计选中数量
    selected_count = db.query(EntityWord).filter(
        and_(
            EntityWord.task_id == task_id,
            EntityWord.is_selected == True,
            EntityWord.is_deleted == False
        )
    ).count()

    return selected_count, added_count, deleted_count


def get_selected_count(db: Session, task_id: str) -> int:
    """查询选中的本体词数量"""
    return db.query(EntityWord).filter(
        and_(
            EntityWord.task_id == task_id,
            EntityWord.is_selected == True,
            EntityWord.is_deleted == False
        )
    ).count()


def get_entity_word_stats(db: Session, task_id: str) -> Dict:
    """
    获取本体词统计信息

    Returns:
        {
            "total_count": 12,
            "selected_count": 6,
            "type_distribution": {"original": 1, "synonym": 3, "variant": 8}
        }
    """
    entity_words = get_entity_words_by_task(db, task_id, include_deleted=False)

    total_count = len(entity_words)
    selected_count = sum(1 for ew in entity_words if ew.is_selected)

    type_distribution = {}
    for ew in entity_words:
        type_distribution[ew.type] = type_distribution.get(ew.type, 0) + 1

    return {
        "total_count": total_count,
        "selected_count": selected_count,
        "type_distribution": type_distribution
    }


def get_selected_entity_words(db: Session, task_id: str) -> List[EntityWord]:
    """查询选中的本体词列表"""
    return db.query(EntityWord).filter(
        and_(
            EntityWord.task_id == task_id,
            EntityWord.is_selected == True,
            EntityWord.is_deleted == False
        )
    ).all()


def soft_delete_all_entity_words(db: Session, task_id: str) -> int:
    """
    软删除任务的所有本体词（用于状态回退）

    Returns:
        删除的数量
    """
    count = db.query(EntityWord).filter(EntityWord.task_id == task_id).update(
        {"is_deleted": True},
        synchronize_session=False
    )
    db.commit()
    return count


def get_all_entity_words(db: Session, task_id: str) -> List[EntityWord]:
    """
    获取所有本体词变体（用于 Negative Keyword）

    Args:
        db: 数据库会话
        task_id: 任务ID

    Returns:
        本体词列表
    """
    return db.query(EntityWord).filter(
        EntityWord.task_id == task_id,
        EntityWord.is_deleted == False
    ).all()

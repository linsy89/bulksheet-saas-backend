"""
TaskAttribute CRUD操作
"""

from sqlalchemy.orm import Session
from app.models_db import TaskAttribute
from typing import List, Dict


def create_attributes_batch(
    db: Session,
    task_id: str,
    attributes: List[Dict]
) -> List[TaskAttribute]:
    """
    批量创建属性词

    Args:
        db: 数据库Session
        task_id: 任务ID
        attributes: 属性词列表，每个元素包含word, concept, type等字段

    Returns:
        创建的TaskAttribute对象列表
    """
    db_attributes = []
    for attr in attributes:
        db_attr = TaskAttribute(
            task_id=task_id,
            word=attr.get("word"),
            concept=attr.get("concept"),
            type=attr.get("type"),
            translation=attr.get("translation", ""),
            use_case=attr.get("use_case", ""),
            search_value=attr.get("search_value", "medium"),
            search_value_stars=attr.get("search_value_stars", 3),
            recommended=attr.get("recommended", True),
            source=attr.get("source", "ai"),
            is_selected=attr.get("is_selected", False),
            is_deleted=False
        )
        db_attributes.append(db_attr)

    db.bulk_save_objects(db_attributes)
    db.commit()
    return db_attributes


def get_attributes_by_task(
    db: Session,
    task_id: str,
    include_deleted: bool = False
) -> List[TaskAttribute]:
    """
    获取任务的所有属性词

    Args:
        db: 数据库Session
        task_id: 任务ID
        include_deleted: 是否包含已删除的属性词

    Returns:
        TaskAttribute对象列表
    """
    query = db.query(TaskAttribute).filter(TaskAttribute.task_id == task_id)

    if not include_deleted:
        query = query.filter(TaskAttribute.is_deleted == False)

    return query.all()


def update_attributes_selection(
    db: Session,
    task_id: str,
    selected_ids: List[int]
) -> int:
    """
    更新属性词的选中状态

    Args:
        db: 数据库Session
        task_id: 任务ID
        selected_ids: 选中的属性词ID列表

    Returns:
        更新的记录数
    """
    # 先将该任务的所有属性词设置为未选中
    db.query(TaskAttribute).filter(
        TaskAttribute.task_id == task_id,
        TaskAttribute.is_deleted == False
    ).update({"is_selected": False})

    # 再将selected_ids中的属性词设置为选中
    if selected_ids:
        count = db.query(TaskAttribute).filter(
            TaskAttribute.id.in_(selected_ids),
            TaskAttribute.task_id == task_id,
            TaskAttribute.is_deleted == False
        ).update({"is_selected": True}, synchronize_session=False)
    else:
        count = 0

    db.commit()
    return count


def soft_delete_attributes(
    db: Session,
    task_id: str,
    attribute_ids: List[int]
) -> int:
    """
    软删除属性词

    Args:
        db: 数据库Session
        task_id: 任务ID
        attribute_ids: 要删除的属性词ID列表

    Returns:
        删除的记录数
    """
    if not attribute_ids:
        return 0

    count = db.query(TaskAttribute).filter(
        TaskAttribute.id.in_(attribute_ids),
        TaskAttribute.task_id == task_id
    ).update({"is_deleted": True, "is_selected": False}, synchronize_session=False)

    db.commit()
    return count


def add_custom_attribute(
    db: Session,
    task_id: str,
    word: str,
    concept: str
) -> TaskAttribute:
    """
    添加用户自定义属性词

    Args:
        db: 数据库Session
        task_id: 任务ID
        word: 属性词
        concept: 原始概念

    Returns:
        创建的TaskAttribute对象
    """
    db_attr = TaskAttribute(
        task_id=task_id,
        word=word,
        concept=concept,
        type="custom",
        translation="用户自定义",
        use_case="用户自定义属性词",
        search_value="medium",
        search_value_stars=3,
        recommended=True,
        source="user",
        is_selected=True,  # 新添加的词默认选中
        is_deleted=False
    )
    db.add(db_attr)
    db.commit()
    db.refresh(db_attr)
    return db_attr


def get_selected_count(db: Session, task_id: str) -> int:
    """
    获取任务中已选中的属性词数量

    Args:
        db: 数据库Session
        task_id: 任务ID

    Returns:
        已选中的属性词数量
    """
    return db.query(TaskAttribute).filter(
        TaskAttribute.task_id == task_id,
        TaskAttribute.is_selected == True,
        TaskAttribute.is_deleted == False
    ).count()

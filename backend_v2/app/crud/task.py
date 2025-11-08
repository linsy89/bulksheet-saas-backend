"""
Task CRUD操作
"""

from sqlalchemy.orm import Session
from app.models_db import Task
from typing import Optional


def create_task(
    db: Session,
    task_id: str,
    concept: str,
    entity_word: str = "phone case"
) -> Task:
    """
    创建任务

    Args:
        db: 数据库Session
        task_id: 任务ID（来自Stage 1）
        concept: 属性概念
        entity_word: 本体词

    Returns:
        创建的Task对象
    """
    db_task = Task(
        task_id=task_id,
        concept=concept,
        entity_word=entity_word,
        status="draft"
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task(db: Session, task_id: str) -> Optional[Task]:
    """
    获取任务

    Args:
        db: 数据库Session
        task_id: 任务ID

    Returns:
        Task对象，如果不存在返回None
    """
    return db.query(Task).filter(Task.task_id == task_id).first()


def update_task_status(db: Session, task_id: str, status: str) -> Optional[Task]:
    """
    更新任务状态

    Args:
        db: 数据库Session
        task_id: 任务ID
        status: 新状态（draft/selected/combined/exported）

    Returns:
        更新后的Task对象，如果不存在返回None
    """
    db_task = get_task(db, task_id)
    if db_task:
        db_task.status = status
        db.commit()
        db.refresh(db_task)
    return db_task


def task_exists(db: Session, task_id: str) -> bool:
    """
    检查任务是否存在

    Args:
        db: 数据库Session
        task_id: 任务ID

    Returns:
        如果存在返回True，否则返回False
    """
    return db.query(Task).filter(Task.task_id == task_id).count() > 0


# ============ Stage 4: 产品信息相关操作 ============

def update_product_info(
    db: Session,
    task_id: str,
    sku: str,
    asin: str,
    model: str
) -> Task:
    """
    更新任务的产品信息

    Args:
        db: 数据库Session
        task_id: 任务ID
        sku: 产品SKU
        asin: 亚马逊ASIN
        model: 手机型号

    Returns:
        更新后的 Task 对象

    Raises:
        ValueError: 任务不存在
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise ValueError(f"任务不存在: {task_id}")

    task.sku = sku
    task.asin = asin
    task.model = model
    db.commit()
    db.refresh(task)

    return task


def get_product_info(db: Session, task_id: str) -> Optional[dict]:
    """
    获取任务的产品信息

    Args:
        db: 数据库Session
        task_id: 任务ID

    Returns:
        {sku, asin, model} 或 None（未保存）

    Raises:
        ValueError: 任务不存在
    """
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise ValueError(f"任务不存在: {task_id}")

    if not task.sku or not task.asin or not task.model:
        return None

    return {
        "sku": task.sku,
        "asin": task.asin,
        "model": task.model
    }

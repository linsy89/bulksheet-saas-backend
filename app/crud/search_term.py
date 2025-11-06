"""
SearchTerm CRUD 操作
搜索词的数据库增删改查
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, delete as sql_delete
from typing import List, Dict, Tuple, Optional
from app.models_db import SearchTerm


def create_search_terms_batch(db: Session, task_id: str, search_terms: List[Dict]) -> int:
    """
    批量创建搜索词

    Args:
        db: 数据库会话
        task_id: 任务ID
        search_terms: 搜索词列表，每个元素包含:
            - term: 完整搜索词
            - attribute_id: 属性词ID
            - attribute_word: 属性词文本
            - entity_word_id: 本体词ID
            - entity_word: 本体词文本
            - length: 字符长度
            - is_valid: 是否有效

    Returns:
        创建的数量
    """
    db_search_terms = []

    for st in search_terms:
        db_search_term = SearchTerm(
            task_id=task_id,
            attribute_id=st["attribute_id"],
            entity_word_id=st["entity_word_id"],
            term=st["term"],
            attribute_word=st["attribute_word"],
            entity_word=st["entity_word"],
            length=st["length"],
            is_valid=st["is_valid"],
            is_deleted=False
        )
        db_search_terms.append(db_search_term)

    db.bulk_save_objects(db_search_terms)
    db.commit()

    return len(db_search_terms)


def get_search_terms_by_task(
    db: Session,
    task_id: str,
    page: int = 1,
    page_size: int = 20,
    filter_by_attribute: Optional[str] = None,
    filter_by_entity: Optional[str] = None,
    include_deleted: bool = False
) -> Tuple[List[SearchTerm], int]:
    """
    分页查询搜索词列表

    Args:
        db: 数据库会话
        task_id: 任务ID
        page: 页码（从1开始）
        page_size: 每页数量
        filter_by_attribute: 按属性词过滤
        filter_by_entity: 按本体词过滤
        include_deleted: 是否包含已删除的搜索词

    Returns:
        (search_terms, total_count)
    """
    query = db.query(SearchTerm).filter(SearchTerm.task_id == task_id)

    if not include_deleted:
        query = query.filter(SearchTerm.is_deleted == False)

    if filter_by_attribute:
        query = query.filter(SearchTerm.attribute_word.contains(filter_by_attribute))

    if filter_by_entity:
        query = query.filter(SearchTerm.entity_word.contains(filter_by_entity))

    # 统计总数
    total_count = query.count()

    # 分页
    offset = (page - 1) * page_size
    search_terms = query.order_by(SearchTerm.id.asc()).offset(offset).limit(page_size).all()

    return search_terms, total_count


def soft_delete_search_terms(db: Session, task_id: str, search_term_ids: List[int]) -> int:
    """
    批量软删除搜索词

    Args:
        db: 数据库会话
        task_id: 任务ID
        search_term_ids: 要删除的搜索词ID列表

    Returns:
        删除的数量
    """
    # 验证所有 ID 是否存在且属于该任务
    existing_ids = db.query(SearchTerm.id).filter(
        and_(
            SearchTerm.id.in_(search_term_ids),
            SearchTerm.task_id == task_id,
            SearchTerm.is_deleted == False
        )
    ).all()

    existing_ids = [id[0] for id in existing_ids]

    if len(existing_ids) != len(search_term_ids):
        invalid_ids = set(search_term_ids) - set(existing_ids)
        raise ValueError(f"以下ID不存在或不属于该任务: {invalid_ids}")

    # 批量软删除（在事务中）
    count = db.query(SearchTerm).filter(
        and_(
            SearchTerm.id.in_(search_term_ids),
            SearchTerm.task_id == task_id
        )
    ).update({"is_deleted": True}, synchronize_session=False)

    db.commit()
    return count


def get_search_term_stats(db: Session, task_id: str) -> Dict:
    """
    获取搜索词统计信息

    Returns:
        {
            "total_terms": 90,
            "valid_terms": 85,
            "invalid_terms": 5
        }
    """
    search_terms = db.query(SearchTerm).filter(
        and_(
            SearchTerm.task_id == task_id,
            SearchTerm.is_deleted == False
        )
    ).all()

    total_terms = len(search_terms)
    valid_terms = sum(1 for st in search_terms if st.is_valid)
    invalid_terms = total_terms - valid_terms

    return {
        "total_terms": total_terms,
        "valid_terms": valid_terms,
        "invalid_terms": invalid_terms
    }


def get_remaining_count(db: Session, task_id: str) -> int:
    """查询剩余的搜索词数量（未删除）"""
    return db.query(SearchTerm).filter(
        and_(
            SearchTerm.task_id == task_id,
            SearchTerm.is_deleted == False
        )
    ).count()


def delete_existing_search_terms(db: Session, task_id: str) -> None:
    """
    实现幂等操作：删除现有搜索词

    1. 物理删除已软删除的记录
    2. 软删除现有有效记录
    """
    # 1. 物理删除已软删除的记录
    db.execute(
        sql_delete(SearchTerm).where(
            and_(
                SearchTerm.task_id == task_id,
                SearchTerm.is_deleted == True
            )
        )
    )

    # 2. 软删除现有有效记录
    db.query(SearchTerm).filter(
        and_(
            SearchTerm.task_id == task_id,
            SearchTerm.is_deleted == False
        )
    ).update({"is_deleted": True}, synchronize_session=False)

    db.commit()


def soft_delete_all_search_terms(db: Session, task_id: str) -> int:
    """
    软删除任务的所有搜索词（用于状态回退）

    Returns:
        删除的数量
    """
    count = db.query(SearchTerm).filter(SearchTerm.task_id == task_id).update(
        {"is_deleted": True},
        synchronize_session=False
    )
    db.commit()
    return count

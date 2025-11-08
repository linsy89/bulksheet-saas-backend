"""
SQLAlchemy ORM 数据库模型
定义tasks和task_attributes表
"""

from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid


class Task(Base):
    """任务主表"""
    __tablename__ = "tasks"

    task_id = Column(
        String(36),  # 使用String存储UUID字符串，兼容SQLite
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    concept = Column(String(200), nullable=False, comment="属性概念")
    entity_word = Column(String(200), nullable=False, default="phone case", comment="本体词")
    status = Column(
        String(50),
        nullable=False,
        default="draft",
        comment="任务状态：draft/selected/combined/exported"
    )

    # Stage 4 新增字段：产品信息
    sku = Column(String(100), nullable=True, comment="产品SKU")
    asin = Column(String(10), nullable=True, comment="亚马逊ASIN")
    model = Column(String(50), nullable=True, comment="手机型号")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系：一个任务有多个属性词
    attributes = relationship("TaskAttribute", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Task(task_id={self.task_id}, concept={self.concept}, status={self.status})>"


class TaskAttribute(Base):
    """任务属性词表"""
    __tablename__ = "task_attributes"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(
        String(36),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="任务ID"
    )

    # 属性词核心字段（8个字段）
    word = Column(String(100), nullable=False, comment="属性词")
    concept = Column(String(200), nullable=False, comment="原始属性词概念")
    type = Column(
        String(50),
        nullable=False,
        comment="词汇类型：original/synonym/related/variant/custom"
    )
    translation = Column(Text, comment="中文翻译和说明")
    use_case = Column(Text, comment="适用场景描述")
    search_value = Column(
        String(20),
        nullable=False,
        comment="搜索价值：high/medium/low"
    )
    search_value_stars = Column(Integer, nullable=False, comment="搜索价值星级：1-5")
    recommended = Column(Boolean, nullable=False, default=True, comment="是否推荐")

    # 扩展字段
    source = Column(
        String(20),
        nullable=False,
        default="ai",
        comment="来源：ai（AI生成）/user（用户添加）"
    )
    is_selected = Column(Boolean, nullable=False, default=False, comment="是否被选中")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="是否已删除（软删除）")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系：多个属性词属于一个任务
    task = relationship("Task", back_populates="attributes")

    def __repr__(self):
        return f"<TaskAttribute(id={self.id}, word={self.word}, selected={self.is_selected})>"


class EntityWord(Base):
    """本体词表（Stage 3）"""
    __tablename__ = "entity_words"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(
        String(36),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="任务ID"
    )

    # 本体词核心字段
    entity_word = Column(String(200), nullable=False, comment="本体词文本")
    concept = Column(String(200), nullable=False, comment="原始属性概念（关联tasks.concept）")
    type = Column(
        String(50),
        nullable=False,
        comment="词汇类型：original/synonym/variant"
    )
    translation = Column(Text, comment="中文翻译和说明")
    use_case = Column(Text, comment="适用场景描述")
    search_value = Column(
        String(20),
        nullable=False,
        comment="搜索价值：high/medium/low"
    )
    search_value_stars = Column(Integer, nullable=False, comment="搜索价值星级：1-5")
    recommended = Column(Boolean, nullable=False, default=True, comment="是否推荐")

    # 扩展字段
    source = Column(
        String(20),
        nullable=False,
        default="ai",
        comment="来源：ai（AI生成）/user（用户添加）"
    )
    is_selected = Column(Boolean, nullable=False, default=True, comment="是否被选中")
    is_deleted = Column(Boolean, nullable=False, default=False, comment="是否已删除（软删除）")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系：多个本体词属于一个任务
    task = relationship("Task", foreign_keys=[task_id])

    def __repr__(self):
        return f"<EntityWord(id={self.id}, entity_word={self.entity_word}, selected={self.is_selected})>"


class SearchTerm(Base):
    """搜索词表（Stage 3）"""
    __tablename__ = "search_terms"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(
        String(36),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="任务ID"
    )

    # 关联字段
    attribute_id = Column(
        Integer,
        ForeignKey("task_attributes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="属性词ID"
    )
    entity_word_id = Column(
        Integer,
        ForeignKey("entity_words.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="本体词ID"
    )

    # 搜索词核心字段
    term = Column(String(300), nullable=False, comment="完整搜索词")
    attribute_word = Column(String(100), nullable=False, comment="属性词文本（冗余）")
    entity_word = Column(String(200), nullable=False, comment="本体词文本（冗余）")
    length = Column(Integer, nullable=False, comment="搜索词字符长度")
    is_valid = Column(Boolean, nullable=False, default=True, comment="是否符合长度要求")

    # 扩展字段
    is_deleted = Column(Boolean, nullable=False, default=False, comment="是否已删除（软删除）")

    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    # 关系
    task = relationship("Task", foreign_keys=[task_id])
    attribute = relationship("TaskAttribute", foreign_keys=[attribute_id])
    entity = relationship("EntityWord", foreign_keys=[entity_word_id])

    def __repr__(self):
        return f"<SearchTerm(id={self.id}, term={self.term}, valid={self.is_valid})>"

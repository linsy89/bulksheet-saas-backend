"""
数据库连接和Session管理
支持PostgreSQL和SQLite
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量获取数据库URL
# 注意：Replit Secrets 会自动注入为系统环境变量，不需要 load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bulksheet.db")

# 配置数据库引擎
# SQLite需要特殊配置check_same_thread
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False  # 设置为True可以看到SQL语句（调试用）
    )
else:
    # PostgreSQL配置
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,  # 连接前检查连接是否有效
        echo=False
    )

# 创建SessionLocal类
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建Base类（所有ORM模型的基类）
Base = declarative_base()


def get_db():
    """
    依赖注入函数：获取数据库Session

    使用方式：
    @app.get("/endpoint")
    def endpoint(db: Session = Depends(get_db)):
        # 使用db进行数据库操作
        pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表（如果不存在）
    """
    # 导入所有模型，确保它们被注册到Base.metadata
    from app import models_db  # noqa: F401

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表初始化完成")

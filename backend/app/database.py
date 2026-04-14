# -*- coding: utf-8 -*-
"""
数据库模型和连接管理
使用 SQLAlchemy + aiosqlite 定义数据表和数据库会话
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, JSON,
    create_engine, event
)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs

from app.config import settings


# 异步引擎
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(AsyncAttrs, DeclarativeBase):
    """SQLAlchemy声明式基类"""
    pass


# 启用SQLite的WAL模式和外键支持
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """设置SQLite连接参数"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseConfig(Base):
    """MySQL数据库连接配置表"""
    __tablename__ = "databases"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    name = Column(String(100), nullable=False, comment="配置名称")
    host = Column(String(255), nullable=False, comment="MySQL主机地址")
    port = Column(Integer, nullable=False, default=3306, comment="MySQL端口")
    username = Column(String(100), nullable=False, comment="MySQL用户名")
    password = Column(Text, nullable=False, comment="MySQL密码（Fernet加密存储）")
    database_name = Column(String(100), default="", comment="默认数据库名")
    # SSH隧道配置
    ssh_host = Column(String(255), default="", comment="SSH主机地址")
    ssh_port = Column(Integer, default=22, comment="SSH端口")
    ssh_username = Column(String(100), default="", comment="SSH用户名")
    ssh_password = Column(Text, default="", comment="SSH密码（Fernet加密存储）")
    ssh_key_file = Column(String(500), default="", comment="SSH私钥文件路径")
    # 其他
    remark = Column(Text, default="", comment="备注")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")


class Inspection(Base):
    """巡检记录表"""
    __tablename__ = "inspections"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    database_id = Column(Integer, nullable=False, comment="关联数据库配置ID")
    status = Column(String(20), nullable=False, default="pending",
                    comment="状态：pending/running/completed/failed")
    health_status = Column(String(20), default="", comment="健康状态：healthy/warning/critical")
    health_score = Column(Float, default=0.0, comment="健康评分(0-100)")
    problem_count = Column(Integer, default=0, comment="问题数量")
    started_at = Column(DateTime, default=None, comment="开始时间")
    completed_at = Column(DateTime, default=None, comment="完成时间")
    report_path = Column(String(500), default="", comment="报告文件路径")
    error_message = Column(Text, default="", comment="错误信息")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


class InspectionResult(Base):
    """巡检结果表"""
    __tablename__ = "inspection_results"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    inspection_id = Column(Integer, nullable=False, comment="关联巡检记录ID")
    category = Column(String(50), nullable=False, comment="结果分类（如：basic_info, performance, security等）")
    key = Column(String(100), nullable=False, comment="结果键名")
    value = Column(JSON, default=dict, comment="结果值（JSON格式）")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")


async def init_db():
    """初始化数据库，创建所有表"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """获取异步数据库会话（依赖注入用）"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
# -*- coding: utf-8 -*-
"""
FastAPI应用入口
创建应用实例，注册中间件、路由，配置启动事件
"""

import os
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db
from app.models import ApiResponse
from app.routers import inspection, database, report

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在初始化数据库...")
    await init_db()
    logger.info("数据库初始化完成")
    logger.info(f"报告存储目录: {settings.REPORT_DIR}")
    logger.info(f"数据库文件: {settings.DATABASE_URL}")

    if not settings.validate_secrets():
        logger.warning("安全警告: 密钥配置不安全，请检查环境变量设置")

    yield
    logger.info("应用正在关闭...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MySQL数据库巡检平台后端API",
    lifespan=lifespan,
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(inspection.router)
app.include_router(database.router)
app.include_router(report.router)

reports_dir = Path(settings.REPORT_DIR)
if reports_dir.exists():
    app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")


@app.get("/", response_model=ApiResponse, tags=["系统"])
async def root():
    """API根路径，返回基本信息"""
    return ApiResponse.success(
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "redoc": "/redoc",
        }
    )


@app.get("/api/health", response_model=ApiResponse, tags=["系统"])
async def health_check():
    """健康检查接口"""
    return ApiResponse.success(data={"status": "healthy", "version": settings.APP_VERSION})
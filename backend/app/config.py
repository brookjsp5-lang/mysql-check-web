# -*- coding: utf-8 -*-
"""
配置管理模块
使用 pydantic-settings 管理应用配置
敏感配置通过环境变量注入，不支持硬编码默认值
"""

import os
import logging
import secrets
import warnings
from pathlib import Path
from typing import Optional, List

from pydantic_settings import BaseSettings
from cryptography.fernet import Fernet


logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """应用配置"""

    APP_NAME: str = "MySQL巡检平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    API_PREFIX: str = "/api"

    DATABASE_DIR: str = str(Path(__file__).parent.parent / "data")
    DATABASE_URL: str = ""

    REPORT_DIR: str = str(Path(__file__).parent.parent / "reports")

    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    ENCRYPTION_KEY: str = ""

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    INSPECTION_TIMEOUT: int = 300
    SSH_TIMEOUT: int = 30
    MYSQL_TIMEOUT: int = 30

    _secret_key_file: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.makedirs(self.DATABASE_DIR, exist_ok=True)
        os.makedirs(self.REPORT_DIR, exist_ok=True)

        if not self.DATABASE_URL:
            self.DATABASE_URL = f"sqlite+aiosqlite:///{self.DATABASE_DIR}/app.db"

        self._init_jwt_secret()
        self._init_encryption_key()

    def _init_jwt_secret(self):
        """初始化JWT密钥，支持环境变量注入"""
        if self.JWT_SECRET_KEY:
            if self.JWT_SECRET_KEY == "mysql-check-web-secret-key-change-in-production":
                if not self.DEBUG:
                    raise ValueError("生产环境必须设置安全的JWT_SECRET_KEY环境变量")
                warnings.warn(
                    "使用默认JWT密钥存在安全风险！请通过环境变量JWT_SECRET_KEY设置强密钥。",
                    RuntimeWarning
                )
            logger.info("JWT密钥已通过环境变量配置")
        else:
            self.JWT_SECRET_KEY = secrets.token_urlsafe(32)
            logger.warning("JWT密钥未设置，已生成随机密钥（仅用于开发环境）")

    def _init_encryption_key(self):
        """初始化加密密钥，支持环境变量注入"""
        if self.ENCRYPTION_KEY:
            try:
                Fernet(self.ENCRYPTION_KEY.encode())
                logger.info("加密密钥已通过环境变量配置")
            except Exception as e:
                raise ValueError(f"环境变量提供的ENCRYPTION_KEY无效: {e}")
        else:
            key_file = os.path.join(self.DATABASE_DIR, ".encryption_key")
            if os.path.exists(key_file):
                with open(key_file, "rb") as f:
                    self.ENCRYPTION_KEY = f.read().decode()
                logger.info("加密密钥已从文件加载")
            else:
                new_key = Fernet.generate_key().decode()
                with open(key_file, "wb") as f:
                    f.write(new_key.encode())
                os.chmod(key_file, 0o600)
                self.ENCRYPTION_KEY = new_key
                logger.warning("未设置加密密钥，已生成新密钥并保存到文件（仅用于开发环境）")

    def get_fernet(self) -> Fernet:
        """获取Fernet加密实例"""
        if not self.ENCRYPTION_KEY:
            raise ValueError("加密密钥未初始化")
        return Fernet(self.ENCRYPTION_KEY.encode())

    def validate_secrets(self) -> bool:
        """验证所有密钥配置是否安全"""
        issues = []

        if not self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
            issues.append("JWT_SECRET_KEY未设置或长度不足32字符")

        default_keys = [
            "mysql-check-web-secret-key-change-in-production",
        ]
        if self.JWT_SECRET_KEY in default_keys:
            issues.append("JWT_SECRET_KEY使用了不安全的默认值")

        if issues:
            for issue in issues:
                warnings.warn(issue, RuntimeWarning)
            return False
        return True


settings = Settings()
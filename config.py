from os import getenv
from typing import Literal


class Config:
    API_PREFIX: str = '/api'
    VERSION: str = '0.0.1'
    PROJECT_NAME: str = 'Test task'
    DEBUG: bool = False

    SECURITY_ACCESS_TOKEN_URL: str = f'{API_PREFIX}/auth/login'
    SECURITY_REFRESH_TOKEN_URL: str = f'{API_PREFIX}/auth/refresh'
    SECURITY_SECRET_KEY: str = getenv('SECRET_KEY')
    SECURITY_ALGORITHM: Literal['HS256'] = 'HS256'
    SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES: int = 120  # 2 hours
    SECURITY_REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days

    SECURITY_REFRESH_TOKEN_COOKIE_KEY: str = "refresh_token"
    SECURITY_REFRESH_TOKEN_COOKIE_EXPIRES: int = 2592000  # seconds
    SECURITY_REFRESH_TOKEN_COOKIE_PATH: str = SECURITY_REFRESH_TOKEN_URL
    SECURITY_REFRESH_TOKEN_COOKIE_DOMAIN: str = '127.0.0.1'
    SECURITY_REFRESH_TOKEN_COOKIE_HTTPONLY: bool = True
    SECURITY_REFRESH_TOKEN_COOKIE_SECURE: bool = True
    SECURITY_REFRESH_TOKEN_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "none"

    MONGO_URL: str = getenv('DATABASE_URL')

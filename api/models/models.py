from typing import List
from datetime import datetime

from api.models.base import Model


class Users(Model):
    username: str
    password: str
    disabled: bool
    created_at: datetime
    last_login_at: datetime
    scopes: List[str]


class Urls(Model):
    url: str
    code: str
    user: str
    expired_at: datetime

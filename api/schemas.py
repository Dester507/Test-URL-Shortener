from typing import Optional, List, Literal

from pydantic import BaseModel


class TokenSchema(BaseModel):
    username: Optional[str] = None
    scopes: List[str] = []


class TokenResponseSchema(BaseModel):
    access_token: str
    token_type: Literal['bearer']


class RegisterSchema(BaseModel):
    username: str
    password: str
    confirm_password: str


class UrlCreateSchema(BaseModel):
    url: str
    days: Optional[int] = None

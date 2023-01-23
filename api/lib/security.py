from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError
from pydantic import ValidationError
from passlib.hash import pbkdf2_sha256

from config import Config
from api.models.models import Users
from api.schemas import TokenSchema
from api.scopes import SUPERUSER_SCOPER, SCOPES


oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=Config.SECURITY_ACCESS_TOKEN_URL,
    scopes=SCOPES
)


async def get_current_user(
        security_scopes: SecurityScopes,
        token: str = Depends(oauth2_schema)
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = 'Bearer'
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': authenticate_value}
    )
    try:
        payload = jwt.decode(token, Config.SECURITY_SECRET_KEY, algorithms=[Config.SECURITY_ALGORITHM])
        username: str = payload.get('sub')
        if not username:
            raise credentials_exception
        token = TokenSchema(scopes=payload.get('scopes', []), username=username)
        user_data = await Users.objects.get(username=token.username)
        if not user_data or user_data['disabled']:
            raise credentials_exception
    except (JWTError, ValidationError):
        raise credentials_exception

    if SUPERUSER_SCOPER not in token.scopes:
        for scope in security_scopes.scopes:
            if scope not in token.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='Not enough permissions',
                    headers={'WWW-Authenticate': authenticate_value}
                )
    return user_data


def create_token(
        data: dict,
        expires_delta: timedelta
):
    data_copy = data.copy()
    expire = datetime.utcnow() + expires_delta
    data_copy.update({'exp': expire})
    encoded = jwt.encode(data_copy, Config.SECURITY_SECRET_KEY, algorithm=Config.SECURITY_ALGORITHM)
    return encoded


def create_user_tokens(user_data):
    access_token_expires = timedelta(minutes=Config.SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=Config.SECURITY_REFRESH_TOKEN_EXPIRE_MINUTES)

    access_token = create_token(
        data={
            'sub': user_data['username'],
            'scopes': user_data['scopes']
        },
        expires_delta=access_token_expires
    )

    refresh_token = create_token(
        data={
            'sub': user_data['username']
        },
        expires_delta=refresh_token_expires
    )
    return access_token, refresh_token


def set_refresh_token_cookie(
        response: Response,
        token: str
):
    response.set_cookie(
        key=Config.SECURITY_REFRESH_TOKEN_COOKIE_KEY,
        value=token,
        expires=Config.SECURITY_REFRESH_TOKEN_COOKIE_EXPIRES,
        path=Config.SECURITY_REFRESH_TOKEN_COOKIE_PATH,
        domain=Config.SECURITY_REFRESH_TOKEN_COOKIE_DOMAIN,
        httponly=Config.SECURITY_REFRESH_TOKEN_COOKIE_HTTPONLY,
        secure=Config.SECURITY_REFRESH_TOKEN_COOKIE_SECURE,
        samesite=Config.SECURITY_REFRESH_TOKEN_COOKIE_SAMESITE
    )


def verify_password(plain_password, hashed_password) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pbkdf2_sha256.hash(password)

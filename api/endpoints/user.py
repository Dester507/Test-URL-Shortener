from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Request, Response, Depends, Security, HTTPException, Cookie, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from api.lib.security import (
    get_current_user,
    verify_password,
    get_password_hash,
    create_user_tokens,
    set_refresh_token_cookie
)
from api.schemas import TokenResponseSchema, RegisterSchema
from api.models.models import Users
from config import Config

router = APIRouter()


@router.post(
    '/login',
    response_model=TokenResponseSchema,
    name='auth:login'
)
async def login(
        request: Request,
        response: Response,
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    user_data = await Users.objects.get(username=form_data.username)
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Bad data.'
    )
    if user_data and verify_password(form_data.password, user_data['password']):
        access_token, refresh_token = create_user_tokens(user_data)
        set_refresh_token_cookie(response, refresh_token)
        await Users.objects.update(
            updated_data={
                'last_login_at': datetime.utcnow()
            },
            username=form_data.username
        )
        return {
            'access_token': access_token,
            'token_type': 'bearer'
        }
    else:
        raise credentials_exception


@router.post(
    '/register',
    name='auth:register'
)
async def register(
        data: RegisterSchema
):
    if len(data.password) < 8 or data.password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad password.'
        )
    if not await Users.objects.get(username=data.username):
        await Users.objects.insert(
            new_data={
                'username': data.username,
                'password': get_password_hash(data.password),
                'disabled': False,
                'created_at': datetime.utcnow(),
                'scopes': ['user']
            }
        )
        return {
            'msg': 'Successfully registered.'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Bad username.'
        )


@router.post(
    '/refresh',
    response_model=TokenResponseSchema,
    name='auth:refresh'
)
async def refresh(
        request: Request,
        response: Response,
        token: Optional[str] = Cookie(None, alias=Config.SECURITY_REFRESH_TOKEN_COOKIE_KEY)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate refresh token.'
    )
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(token, Config.SECURITY_SECRET_KEY, algorithms=[Config.SECURITY_ALGORITHM])
        username = payload.get('sub')
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user_data = await Users.objects.get(username=username)
    if not user_data:
        raise credentials_exception
    access_token, refresh_token = create_user_tokens(user_data)
    set_refresh_token_cookie(response, refresh_token)
    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }


@router.post(
    '/logout',
    name='auth:logout'
)
async def logout(
        response: Response,
        user=Security(get_current_user)
):
    response.delete_cookie(
        Config.SECURITY_REFRESH_TOKEN_COOKIE_KEY,
        Config.SECURITY_REFRESH_TOKEN_COOKIE_PATH,
        Config.SECURITY_REFRESH_TOKEN_COOKIE_DOMAIN
    )
    return {
        'msg': 'Successfully logged out.'
    }

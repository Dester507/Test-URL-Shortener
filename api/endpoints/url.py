from random import choices
from string import ascii_lowercase, ascii_uppercase, digits
from datetime import datetime, timedelta

from fastapi import APIRouter, Security, HTTPException, status
from fastapi.responses import RedirectResponse

from api.models.models import Urls
from api.lib.security import get_current_user
from api.schemas import UrlCreateSchema


router = APIRouter()


def generate_code() -> str:
    return ''.join(choices(ascii_lowercase + digits + ascii_uppercase, k=6))


async def get_code() -> str:
    code = generate_code()
    while await Urls.objects.get(code=code):
        code = get_code()
    return code


@router.post(
    '/',
    name='url:create'
)
async def create_short_url(
        data: UrlCreateSchema,
        user=Security(get_current_user, scopes=['user'])
):
    code = await get_code()
    if not data.days or data.days < 1 or data.days > 365:
        days = 90
    else:
        days = data.days
    await Urls.objects.insert(
        new_data={
            'url': data.url,
            'code': code,
            'user': user['username'],
            'expired_at': datetime.utcnow() + timedelta(days=days)
        }
    )
    return {
        'msg': 'Successfully created.',
        'code': code
    }


@router.get(
    '/{code}',
    name='url:redirect'
)
async def code_redirect(
        code: str
):
    credential_exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Not found.'
    )
    if url_data := await Urls.objects.get(code=code):
        if url_data['expired_at'] < datetime.utcnow():
            await Urls.objects.delete(
                filter_data={
                    'code': code
                }
            )
            raise credential_exception
        else:
            return RedirectResponse(url_data['url'])
    else:
        raise credential_exception

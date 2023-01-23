from fastapi import APIRouter

from api.endpoints import (
    url,
    user
)
from config import Config


router = APIRouter()

router.include_router(url.router, tags=['url-endpoints'])
router.include_router(user.router, tags=['user-endpoints'], prefix=f'{Config.API_PREFIX}/auth')

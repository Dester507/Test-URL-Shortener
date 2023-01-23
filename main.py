from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from config import Config
from api import router


def create_application() -> FastAPI:
    application = FastAPI(
        title=Config.PROJECT_NAME,
        debug=Config.DEBUG,
        version=Config.VERSION,
        docs_url=f'{Config.API_PREFIX}/docs',
        redoc_url=f'{Config.API_PREFIX}/redoc',
        openapi_url=f'{Config.API_PREFIX}/openapi.json'
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*']
    )
    application.include_router(router)
    return application


app = create_application()

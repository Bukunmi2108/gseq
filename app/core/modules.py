# fastapi 
from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# import 
from app.core.base import engine
from app.api.routers.main_router import router
from app.core.settings import settings

def init_routers(app_: FastAPI) -> None:
    app_.include_router(router, prefix=settings.API_V1_STR)

origins = [
    "*",
	# "http://localhost.tiangolo.com",
	# "https://localhost.tiangolo.com",
	# "http://localhost",
	# "http://localhost:8080",
]

def make_middleware() -> List[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        # Middleware(SQLAlchemyMiddleware),
    ]
    return middleware
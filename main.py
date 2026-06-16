from fastapi import FastAPI
from sqlalchemy import text

from api.route import router
from core.database import Base, DATABASE_URL, engine
from core.exception_handler import app_exception_handler
from core.exceptions import AppException

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(AppException, app_exception_handler)
    return app

app = create_app()

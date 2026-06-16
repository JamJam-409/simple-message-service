from fastapi import FastAPI

from app.routes import router
from app.exceptions import app_exception_handler
from app.exceptions import AppException

def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router)
    app.add_exception_handler(AppException, app_exception_handler)
    return app

app = create_app()

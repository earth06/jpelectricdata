from pathlib import Path

import plotly
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.web.routes import router as web_router

app = FastAPI(title=settings.app_name)

app.include_router(api_router)
app.include_router(web_router)

plotly_package_data = Path(plotly.__file__).resolve().parent / "package_data"
app.mount("/static/vendor/plotly", StaticFiles(directory=plotly_package_data), name="plotly-static")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

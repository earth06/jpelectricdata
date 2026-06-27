from fastapi import APIRouter

from app.api.v1.routers import charts, demand_supply, export, spot_price

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(spot_price.router)
api_router.include_router(demand_supply.router)
api_router.include_router(charts.router)
api_router.include_router(export.router)

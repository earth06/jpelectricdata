from datetime import date

from fastapi import APIRouter, HTTPException

from app.services.chart_service import chart_service

router = APIRouter(prefix="/charts", tags=["charts"])


@router.get("/home/price")
def home_price(base_date: date) -> dict:
    """Return Plotly figure JSON for the home price chart."""
    try:
        return {"figure": chart_service.home_price(base_date)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/home/demand")
def home_demand(base_date: date, field: str = "area_demand") -> dict:
    """Return Plotly figure JSON for the home demand/supply chart."""
    try:
        return {"figure": chart_service.home_demand(base_date, field)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/balance/price")
def balance_price(base_date: date) -> dict:
    """Return Plotly figure JSON for the balance price chart."""
    try:
        return {"figure": chart_service.balance_price(base_date)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/balance/supply")
def balance_supply(base_date: date, area: str = "chubu") -> dict:
    """Return Plotly figure JSON for the balance supply chart."""
    try:
        return {"figure": chart_service.balance_supply(base_date, area)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/trend/spot")
def trend_spot(base_date: date, spot_type: str = "price") -> dict:
    """Return Plotly figure JSON for the trend spot chart."""
    try:
        return {"figure": chart_service.trend_spot(base_date, spot_type)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/trend/supply")
def trend_supply(base_date: date, area: str = "chubu") -> dict:
    """Return Plotly figure JSON for the trend supply chart."""
    try:
        return {"figure": chart_service.trend_supply(base_date, area)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

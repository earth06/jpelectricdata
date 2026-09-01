from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from app.core.chart_config import AREA_JP_NAMES, DEMAND_SUPPLY_JP_NAMES, NAVIGATION, TREND_AREA_JP_NAMES
from app.services.electric_service import electric_service

router = APIRouter()
templates = Jinja2Templates(directory="app/web/templates")


def _context(request: Request, page: str, title: str) -> dict:
    """Return common template context for dashboard pages."""
    today = datetime.now(tz=ZoneInfo("Asia/Tokyo")).date()
    chart_base_date = electric_service.latest_chart_base_date() or today
    return {
        "request": request,
        "page": page,
        "title": title,
        "navigation": NAVIGATION,
        "today": today.isoformat(),
        "chart_base_date": chart_base_date.isoformat(),
        "two_days_before_chart_base": (chart_base_date - timedelta(days=2)).isoformat(),
        "default_start": date(2024, 12, 1).isoformat(),
        "default_end": date(2024, 12, 7).isoformat(),
        "demand_supply_options": DEMAND_SUPPLY_JP_NAMES,
        "area_options": AREA_JP_NAMES,
        "trend_area_options": TREND_AREA_JP_NAMES,
    }


@router.get("/")
def home(request: Request):
    """Render the home dashboard page."""
    return templates.TemplateResponse(request, "home.html", _context(request, "home", "ホーム"))


@router.get("/balance")
def balance(request: Request):
    """Render the demand/supply balance page."""
    return templates.TemplateResponse(request, "balance.html", _context(request, "balance", "需給バランス"))


@router.get("/trend")
def trend(request: Request):
    """Render the monthly trend page."""
    return templates.TemplateResponse(request, "trend.html", _context(request, "trend", "1か月トレンド"))


@router.get("/download")
def download(request: Request):
    """Render the spot price download page."""
    return templates.TemplateResponse(request, "download.html", _context(request, "download", "ダウンロード"))


@router.get("/publishapiurl")
def publish_api_url(request: Request):
    """Render the API URL generator page."""
    return templates.TemplateResponse(request, "publishapiurl.html", _context(request, "publishapiurl", "API URL発行"))


@router.get("/powermap")
def powermap(request: Request):
    """Render the power transmission WebGIS page."""
    context = _context(request, "powermap", "送電線マップ")
    context["powermap_config"] = {
        "tileJsonUrl": "/api/v1/powermap/tilejson.json",
        "initialViewState": {
            "longitude": 136.881537,
            "latitude": 35.170915,
            "zoom": 10,
            "pitch": 0,
            "bearing": 0,
        },
    }
    return templates.TemplateResponse(request, "powermap.html", context)

from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.services.electric_service import electric_service

router = APIRouter(prefix="/spot-prices", tags=["spot-prices"])


@router.get("")
def read_spot_prices(
    *,
    begin: date,
    end: date,
    areas: Annotated[str | None, Query(description="Comma-separated area names")] = None,
    fields: Annotated[str | None, Query(description="Comma-separated spot_price columns")] = None,
) -> list[dict]:
    """Return spot market data for the requested date range."""
    try:
        return electric_service.spot_prices(begin=begin, end=end, areas=areas, fields=fields)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

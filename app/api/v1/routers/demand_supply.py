from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.services.electric_service import electric_service

router = APIRouter(prefix="/demand-supply", tags=["demand-supply"])


@router.get("")
def read_demand_supply(
    *,
    begin: date,
    end: date,
    area: Annotated[str | None, Query(description="Area name")] = None,
    fields: Annotated[str | None, Query(description="Comma-separated demand/supply columns")] = None,
    ignore_negative: bool = False,
) -> list[dict]:
    """Return demand/supply data for the requested date range."""
    try:
        return electric_service.demand_supply(
            begin=begin,
            end=end,
            area=area,
            fields=fields,
            ignore_negative=ignore_negative,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

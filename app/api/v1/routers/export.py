from datetime import date
from io import StringIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.electric_service import electric_service

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/spot-prices.csv")
def export_spot_prices(begin: date, end: date) -> StreamingResponse:
    """Download spot market data as CSV."""
    try:
        csv_text = electric_service.spot_prices_csv(begin=begin, end=end)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    headers = {"Content-Disposition": 'attachment; filename="spot-prices.csv"'}
    return StreamingResponse(
        StringIO(csv_text),
        media_type="text/csv; charset=utf-8",
        headers=headers,
    )

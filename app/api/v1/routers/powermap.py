from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.services.power_tile_service import MVT_CONTENT_TYPE, power_tile_service

router = APIRouter(prefix="/powermap", tags=["powermap"])


@router.get("/metadata")
def metadata() -> dict[str, Any]:
    """Return MBTiles metadata for the power map."""
    raw_metadata = power_tile_service.metadata()
    return {
        "metadata": raw_metadata,
        "json": power_tile_service.parsed_json_metadata(raw_metadata),
    }


@router.get("/tilejson.json")
def tilejson(request: Request) -> dict[str, Any]:
    """Return TileJSON for MapLibre vector tile source."""
    return power_tile_service.tilejson(request)


@router.get("/tiles/{z}/{x}/{y}.pbf")
def get_tile(z: int, x: int, y: int) -> Response:
    """Return one XYZ vector tile from data/power.mbtiles."""
    tile_data, headers = power_tile_service.tile(z=z, x=x, y=y)
    return Response(content=tile_data, media_type=MVT_CONTENT_TYPE, headers=headers)

import json
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import HTTPException, Request

from app.core.config import settings

MVT_CONTENT_TYPE = "application/vnd.mapbox-vector-tile"
GZIP_MAGIC_NUMBER = "1F8B"
NOT_FOUND_MESSAGE = "tile not found"
INVALID_COORDINATE_MESSAGE = "invalid tile coordinate"
MISSING_MBTILES_MESSAGE = "MBTiles file is missing"


class PowerTileService:
    """Read power WebGIS vector tiles from an MBTiles file."""

    def __init__(self, mbtiles_path: Path | None = None) -> None:
        self.mbtiles_path = mbtiles_path or settings.power_mbtiles_path

    def connect(self) -> sqlite3.Connection:
        """Open the MBTiles database in read-only mode."""
        if not self.mbtiles_path.exists():
            raise HTTPException(status_code=500, detail=MISSING_MBTILES_MESSAGE)
        connection = sqlite3.connect(f"file:{self.mbtiles_path}?mode=ro", uri=True)
        connection.row_factory = sqlite3.Row
        return connection

    def metadata(self) -> dict[str, str]:
        """Return raw MBTiles metadata."""
        with self.connect() as connection:
            rows = connection.execute("SELECT name, value FROM metadata").fetchall()
        return {row["name"]: row["value"] for row in rows}

    def parsed_json_metadata(self, metadata: dict[str, str] | None = None) -> dict[str, Any]:
        """Return the parsed MBTiles json metadata object."""
        raw_json = (metadata or self.metadata()).get("json")
        if raw_json is None:
            return {}
        return json.loads(raw_json)

    def tilejson(self, request: Request) -> dict[str, Any]:
        """Return TileJSON for the power vector tile source."""
        metadata = self.metadata()
        parsed_json = self.parsed_json_metadata(metadata)
        tilejson: dict[str, Any] = {
            "tilejson": "3.0.0",
            "name": metadata.get("name", self.mbtiles_path.stem),
            "description": metadata.get("description", ""),
            "version": metadata.get("version", "1"),
            "scheme": "xyz",
            "tiles": [f"{str(request.base_url).rstrip('/')}/api/v1/powermap/tiles/{{z}}/{{x}}/{{y}}.pbf"],
            "format": metadata.get("format", "pbf"),
        }
        for key in ("bounds", "center"):
            values = self._parse_float_list(metadata.get(key))
            if values is not None:
                tilejson[key] = values
        for key in ("minzoom", "maxzoom"):
            value = self._parse_int(metadata.get(key))
            if value is not None:
                tilejson[key] = value
        if "vector_layers" in parsed_json:
            tilejson["vector_layers"] = parsed_json["vector_layers"]
        return tilejson

    def tile(self, z: int, x: int, y: int) -> tuple[bytes, dict[str, str]]:
        """Return one vector tile and response headers."""
        metadata = self.metadata()
        self._validate_coordinate(z, x, y, metadata)
        tms_y = (1 << z) - 1 - y
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT tile_data
                FROM tiles
                WHERE zoom_level = ? AND tile_column = ? AND tile_row = ?
                """,
                (z, x, tms_y),
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE)

        tile_data = row["tile_data"]
        headers = {"Cache-Control": "public, max-age=3600"}
        if tile_data.hex().upper().startswith(GZIP_MAGIC_NUMBER):
            headers["Content-Encoding"] = "gzip"
        return tile_data, headers

    def _validate_coordinate(self, z: int, x: int, y: int, metadata: dict[str, str]) -> None:
        """Validate tile coordinates against metadata zoom range and XYZ bounds."""
        minzoom = self._parse_int(metadata.get("minzoom"))
        maxzoom = self._parse_int(metadata.get("maxzoom"))
        max_index = (1 << z) - 1
        if minzoom is not None and z < minzoom:
            raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE)
        if maxzoom is not None and z > maxzoom:
            raise HTTPException(status_code=404, detail=NOT_FOUND_MESSAGE)
        if x < 0 or y < 0 or x > max_index or y > max_index:
            raise HTTPException(status_code=400, detail=INVALID_COORDINATE_MESSAGE)

    def _parse_int(self, value: str | None) -> int | None:
        """Parse an optional integer metadata value."""
        if value is None:
            return None
        return int(value)

    def _parse_float_list(self, value: str | None) -> list[float] | None:
        """Parse comma-separated float metadata values."""
        if value is None:
            return None
        return [float(item) for item in value.split(",")]


power_tile_service = PowerTileService()

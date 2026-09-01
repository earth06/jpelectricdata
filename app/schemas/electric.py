from typing import Literal

from pydantic import BaseModel, Field

Area = Literal[
    "hokkaido",
    "tohoku",
    "tokyo",
    "chubu",
    "hokuriku",
    "kansai",
    "chugoku",
    "shikoku",
    "kyusyu",
]
TrendArea = Area | Literal["all"]
SpotType = Literal["price", "block"]


class SpotPriceRecord(BaseModel):
    """Spot price row returned by the API."""

    date_time: str
    values: dict[str, float | int | str | None] = Field(default_factory=dict)


class DemandSupplyRecord(BaseModel):
    """Demand/supply row returned by the API."""

    date_time: str
    area_name: str | None = None
    values: dict[str, float | int | str | None] = Field(default_factory=dict)


class ChartResponse(BaseModel):
    """Plotly figure payload."""

    figure: dict

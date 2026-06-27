from datetime import date, timedelta
from typing import Any

import pandas as pd

from app.core.chart_config import (
    AREAS,
    DEMAND_SUPPLY_NAMES,
    SPOT_BLOCK_COLUMNS,
    TARGET_AREAS,
    spot_price_columns,
)
from app.data_access.electric_data import ElectricDataAccess


class ElectricService:
    """Prepare validated electricity data for APIs and charts."""

    def __init__(self, data_access: ElectricDataAccess | None = None) -> None:
        self.data_access = data_access or ElectricDataAccess()

    def validate_date_range(self, begin: date, end: date) -> None:
        """Validate that a date range is ordered."""
        if begin > end:
            msg = "begin must be earlier than or equal to end"
            raise ValueError(msg)

    def resolve_areas(self, areas: str | None) -> list[str]:
        """Parse comma-separated areas, defaulting to target areas."""
        if areas is None or areas == "":
            return TARGET_AREAS
        values = [value.strip() for value in areas.split(",") if value.strip()]
        unknown = sorted(set(values) - set(AREAS))
        if unknown:
            msg = f"Unknown areas: {', '.join(unknown)}"
            raise ValueError(msg)
        return values

    def resolve_fields(self, fields: str | None, allowed: list[str]) -> list[str] | None:
        """Parse comma-separated field names and validate them."""
        if fields is None or fields == "":
            return None
        values = [value.strip() for value in fields.split(",") if value.strip()]
        unknown = sorted(set(values) - set(allowed))
        if unknown:
            msg = f"Unknown fields: {', '.join(unknown)}"
            raise ValueError(msg)
        return values

    def spot_prices(
        self,
        begin: date,
        end: date,
        areas: str | None = None,
        fields: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return spot price rows for the API."""
        self.validate_date_range(begin, end)
        selected_areas = self.resolve_areas(areas)
        allowed_fields = [
            "slot",
            "sell_amount",
            "buy_amount",
            "contract_amount",
            "system_price",
            *spot_price_columns(AREAS),
            *SPOT_BLOCK_COLUMNS,
        ]
        selected_fields = self.resolve_fields(fields, allowed_fields)
        columns = ["date_time", *(selected_fields or spot_price_columns(selected_areas))]
        return self.data_access.read_spot_prices(begin, end, columns=columns)

    def demand_supply(
        self,
        begin: date,
        end: date,
        area: str | None = None,
        fields: str | None = None,
        *,
        ignore_negative: bool = False,
    ) -> list[dict[str, Any]]:
        """Return demand/supply rows for the API."""
        self.validate_date_range(begin, end)
        if area and area not in AREAS:
            msg = f"Unknown area: {area}"
            raise ValueError(msg)
        selected_fields = self.resolve_fields(fields, DEMAND_SUPPLY_NAMES)
        columns = ["date_time", "area_name", *(selected_fields or DEMAND_SUPPLY_NAMES)]
        rows = self.data_access.read_demand_supply(begin, end, columns=columns, area=area)
        if ignore_negative:
            rows = self._replace_negative_values(rows, selected_fields or DEMAND_SUPPLY_NAMES)
        return rows

    def spot_prices_csv(self, begin: date, end: date) -> str:
        """Return all spot price rows as CSV text."""
        rows = self.data_access.read_spot_prices(begin, end)
        if not rows:
            return ""
        return pd.DataFrame(rows).to_csv(index=False)

    def chart_range(self, base_date: date, days: int) -> tuple[date, date]:
        """Return the begin/end dates used by the old Dash chart callbacks."""
        return base_date - timedelta(days=days), base_date

    def latest_chart_base_date(self) -> date | None:
        """Return the latest base date that can render both spot and demand charts."""
        return self.data_access.latest_common_chart_date() or self.data_access.latest_demand_supply_date()

    def spot_price_frame(
        self,
        begin: date,
        end: date,
        columns: list[str] | None = None,
    ) -> pd.DataFrame:
        """Return spot prices as a DataFrame for chart generation."""
        rows = self.data_access.read_spot_prices(begin, end, columns=columns)
        return pd.DataFrame(rows)

    def demand_supply_frame(
        self,
        begin: date,
        end: date,
        area: str | None = None,
        *,
        ignore_negative: bool = False,
    ) -> pd.DataFrame:
        """Return demand/supply values as a DataFrame for chart generation."""
        rows = self.demand_supply(begin, end, area=area, ignore_negative=ignore_negative)
        return pd.DataFrame(rows)

    def _replace_negative_values(
        self,
        rows: list[dict[str, Any]],
        columns: list[str],
    ) -> list[dict[str, Any]]:
        """Replace negative demand/supply measurements with zero."""
        for row in rows:
            for column in columns:
                value = row.get(column)
                if isinstance(value, int | float) and value < 0:
                    row[column] = 0
        return rows


electric_service = ElectricService()

import json
from datetime import date
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from app.core.chart_config import (
    AREA_JP_NAMES,
    DEMAND_SUPPLY_JP_NAMES,
    SPOT_BLOCK_COLUMNS,
    SUPPLY_COLORS,
    SUPPLY_NAMES,
    TARGET_AREAS,
    TREND_AREA_JP_NAMES,
    apply_chart_theme,
    format_legend,
    spot_price_columns,
)
from app.services.electric_service import ElectricService, electric_service


class ChartService:
    """Build Plotly figures compatible with the old Dash charts."""

    def __init__(self, service: ElectricService = electric_service) -> None:
        self.service = service

    def home_price(self, base_date: date) -> dict[str, Any]:
        """Build the home page spot price chart."""
        begin, end = self.service.chart_range(base_date, 7)
        columns = ["date_time", *spot_price_columns(TARGET_AREAS)]
        spot_frame = self._spot_frame(begin, end, columns)
        fig = px.line(spot_frame, x="date_time", y=spot_price_columns(TARGET_AREAS))
        format_legend(fig)
        apply_chart_theme(fig)
        fig.update_layout(title="スポット市場価格")
        return self._figure_json(fig)

    def home_demand(self, base_date: date, field: str) -> dict[str, Any]:
        """Build the home page demand/supply line chart."""
        if field not in DEMAND_SUPPLY_JP_NAMES:
            msg = f"Unknown demand/supply field: {field}"
            raise ValueError(msg)
        begin, end = self.service.chart_range(base_date, 7)
        demand_frame = self.service.demand_supply_frame(begin, end)
        fig = px.line(demand_frame, x="date_time", y=field, color="area_name")
        format_legend(fig)
        apply_chart_theme(fig)
        fig.update_layout(title=DEMAND_SUPPLY_JP_NAMES[field])
        return self._figure_json(fig)

    def balance_price(self, base_date: date) -> dict[str, Any]:
        """Build the balance page spot price chart."""
        return self.home_price(base_date)

    def balance_supply(self, base_date: date, area: str) -> dict[str, Any]:
        """Build the balance page stacked supply chart."""
        if area not in AREA_JP_NAMES:
            msg = f"Unknown area: {area}"
            raise ValueError(msg)
        begin, end = self.service.chart_range(base_date, 7)
        demand_frame = self.service.demand_supply_frame(begin, end, area=area, ignore_negative=True)
        fig = self._stacked_supply_figure(demand_frame)
        format_legend(fig)
        apply_chart_theme(fig)
        fig.update_layout(title=f"{AREA_JP_NAMES[area]}:需給")
        return self._figure_json(fig)

    def trend_spot(self, base_date: date, spot_type: str) -> dict[str, Any]:
        """Build the trend page spot market chart."""
        begin, end = self.service.chart_range(base_date, 30)
        if spot_type == "price":
            columns = spot_price_columns(TARGET_AREAS)
        elif spot_type == "block":
            columns = SPOT_BLOCK_COLUMNS
        else:
            msg = f"Unknown spot_type: {spot_type}"
            raise ValueError(msg)
        spot_frame = self._spot_frame(begin, end, ["date_time", *columns])
        fig = px.line(
            spot_frame,
            x="date_time",
            y=columns,
            color_discrete_sequence=["red", "pink", "blue", "aqua"],
        )
        format_legend(fig)
        fig.update_layout(
            height=500,
            title="スポット市場価格",
            yaxis={"fixedrange": False},
            xaxis={"rangeslider": {"visible": True, "thickness": 0.1}, "type": "date"},
        )
        apply_chart_theme(fig)
        return self._figure_json(fig)

    def trend_supply(self, base_date: date, area: str) -> dict[str, Any]:
        """Build the trend page stacked supply chart."""
        if area not in TREND_AREA_JP_NAMES:
            msg = f"Unknown area: {area}"
            raise ValueError(msg)
        begin, end = self.service.chart_range(base_date, 30)
        if area == "all":
            demand_frame = self.service.demand_supply_frame(begin, end, ignore_negative=True)
            if not demand_frame.empty:
                demand_frame = demand_frame.groupby("date_time", as_index=False)[[*SUPPLY_NAMES, "area_demand"]].sum()
        else:
            demand_frame = self.service.demand_supply_frame(begin, end, area=area, ignore_negative=True)
        fig = self._stacked_supply_figure(demand_frame)
        format_legend(fig)
        fig.update_layout(
            height=500,
            title=f"{TREND_AREA_JP_NAMES[area]}:需給",
            yaxis={"fixedrange": False},
            xaxis={"rangeslider": {"visible": True, "thickness": 0.1}, "type": "date"},
        )
        apply_chart_theme(fig)
        return self._figure_json(fig)

    def _stacked_supply_figure(self, supply_frame: pd.DataFrame):
        """Build a stacked supply figure with area demand overlay."""
        supply_frame = self._ensure_columns(supply_frame, ["date_time", *SUPPLY_NAMES, "area_demand"])
        fig = px.area(
            supply_frame,
            x="date_time",
            y=SUPPLY_NAMES,
            color_discrete_sequence=SUPPLY_COLORS,
        )
        for trace in fig.data:
            if getattr(trace, "fill", None) in ("tonexty", "tozeroy"):
                trace.update(line={"width": 0.4}, opacity=0.85)
        fig.add_trace(
            go.Scatter(
                x=supply_frame["date_time"],
                y=supply_frame["area_demand"],
                name="エリア需要",
                line={"color": "#1e3a8a", "width": 3},
            ),
        )
        return fig

    def _spot_frame(self, begin: date, end: date, columns: list[str]) -> pd.DataFrame:
        """Return a spot price frame with required chart columns."""
        spot_frame = self.service.spot_price_frame(begin, end, columns=columns)
        return self._ensure_columns(spot_frame, columns)

    def _ensure_columns(self, df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
        """Ensure an empty DataFrame still has columns expected by Plotly."""
        if df.empty:
            return pd.DataFrame(columns=columns)
        for column in columns:
            if column not in df.columns:
                df[column] = None
        return df

    def _figure_json(self, fig) -> dict[str, Any]:
        """Return a JSON-serializable Plotly figure dict."""
        return json.loads(fig.to_json())


chart_service = ChartService()

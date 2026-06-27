from datetime import date, datetime, time
from typing import Any

from sqlalchemy import Column, Float, Integer, MetaData, String, Table, select
from sqlalchemy.engine import Engine

from app.core.chart_config import DEMAND_SUPPLY_NAMES
from app.db.session import engine

metadata = MetaData()

spot_price = Table(
    "spot_price",
    metadata,
    Column("date_time", String, primary_key=True),
    Column("slot", Integer),
    Column("sell_amount", Float),
    Column("buy_amount", Float),
    Column("contract_amount", Float),
    Column("system_price", Float),
    Column("area_price_hokkaido", Float),
    Column("area_price_tohoku", Float),
    Column("area_price_tokyo", Float),
    Column("area_price_chubu", Float),
    Column("area_price_hokuriku", Float),
    Column("area_price_kansai", Float),
    Column("area_price_chugoku", Float),
    Column("area_price_shikoku", Float),
    Column("area_price_kyusyu", Float),
    Column("sell_block_amount", Float),
    Column("sell_block_contract_amount", Float),
    Column("buy_block_amount", Float),
    Column("buy_block_contract_amount", Float),
)

detail_demand_supply = Table(
    "detail_demand_supply",
    metadata,
    Column("date_time", String, primary_key=True),
    Column("area_name", String, primary_key=True),
    Column("area_demand", Float),
    Column("nuclear", Float),
    Column("thermal_lng", Float),
    Column("thermal_coal", Float),
    Column("thermal_oil", Float),
    Column("thermal_others", Float),
    Column("hydropower", Float),
    Column("geothermal", Float),
    Column("biomass", Float),
    Column("solarpower", Float),
    Column("soloarcontrol", Float),
    Column("windpower", Float),
    Column("windcontrol", Float),
    Column("pumping_up", Float),
    Column("battery", Float),
    Column("connector", Float),
    Column("others", Float),
    Column("total", Float),
)


def _day_bounds(begin: date, end: date) -> tuple[str, str]:
    """Return SQLite text bounds for an inclusive date range."""
    start = datetime.combine(begin, time.min).strftime("%Y-%m-%d %H:%M")
    finish = datetime.combine(end, time(hour=23, minute=59)).strftime("%Y-%m-%d %H:%M")
    return start, finish


def _validate_columns(table: Table, columns: list[str]) -> list[str]:
    """Validate requested column names against a SQLAlchemy table."""
    unknown = sorted(set(columns) - set(table.c.keys()))
    if unknown:
        joined = ", ".join(unknown)
        msg = f"Unknown columns: {joined}"
        raise ValueError(msg)
    return columns


class ElectricDataAccess:
    """Read electricity data from SQLite via SQLAlchemy Core."""

    def __init__(self, db_engine: Engine = engine) -> None:
        self.engine = db_engine

    def read_spot_prices(
        self,
        begin: date,
        end: date,
        columns: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Read spot price rows for an inclusive date range."""
        start, finish = _day_bounds(begin, end)
        selected_names = columns or list(spot_price.c.keys())
        selected_names = _validate_columns(spot_price, selected_names)
        selected_columns = [spot_price.c[name] for name in selected_names]
        statement = (
            select(*selected_columns)
            .where(spot_price.c.date_time.between(start, finish))
            .order_by(spot_price.c.date_time)
        )
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings()]

    def read_demand_supply(
        self,
        begin: date,
        end: date,
        columns: list[str] | None = None,
        area: str | None = None,
    ) -> list[dict[str, Any]]:
        """Read demand/supply rows for an inclusive date range."""
        start, finish = _day_bounds(begin, end)
        base_columns = ["date_time", "area_name"]
        selected_names = columns or [*base_columns, *DEMAND_SUPPLY_NAMES]
        selected_names = _validate_columns(detail_demand_supply, selected_names)
        selected_columns = [detail_demand_supply.c[name] for name in selected_names]
        statement = (
            select(*selected_columns)
            .where(detail_demand_supply.c.date_time.between(start, finish))
            .order_by(detail_demand_supply.c.date_time, detail_demand_supply.c.area_name)
        )
        if area:
            statement = statement.where(detail_demand_supply.c.area_name == area)
        with self.engine.connect() as connection:
            return [dict(row) for row in connection.execute(statement).mappings()]

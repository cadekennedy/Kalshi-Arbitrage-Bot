from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from pydantic import BaseModel, ConfigDict


class MarketDataError(ValueError):
    """Raised when raw Kalshi market data cannot be converted."""


class Market(BaseModel):
    model_config = ConfigDict(frozen=True)

    ticker: str
    event_ticker: str | None = None
    title: str
    status: str

    open_time: datetime | None = None
    close_time: datetime | None = None

    yes_bid: Decimal | None = None
    yes_ask: Decimal | None = None
    no_bid: Decimal | None = None
    no_ask: Decimal | None = None
    last_price: Decimal | None = None

    volume: Decimal | None = None
    open_interest: Decimal | None = None

    @classmethod
    def from_kalshi(cls, data: dict[str, Any]) -> "Market":
        try:
            return cls(
                ticker=data["ticker"],
                event_ticker=data.get("event_ticker"),
                title=data["title"],
                status=data["status"],
                open_time=data.get("open_time"),
                close_time=data.get("close_time"),
                yes_bid=_to_decimal(data.get("yes_bid_dollars")),
                yes_ask=_to_decimal(data.get("yes_ask_dollars")),
                no_bid=_to_decimal(data.get("no_bid_dollars")),
                no_ask=_to_decimal(data.get("no_ask_dollars")),
                last_price=_to_decimal(data.get("last_price_dollars")),
                volume=_to_decimal(data.get("volume_fp")),
                open_interest=_to_decimal(data.get("open_interest_fp")),
            )

        except KeyError as exc:
            raise MarketDataError(
                f"Required Kalshi market field is missing: {exc.args[0]}"
            ) from exc

        except (ValueError, InvalidOperation) as exc:
            raise MarketDataError("Invalid Kalshi market data.") from exc


def _to_decimal(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None

    return Decimal(str(value))

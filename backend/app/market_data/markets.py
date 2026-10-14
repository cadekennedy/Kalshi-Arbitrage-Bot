from app.market_data.client import KalshiClient
from app.models.market import Market


class MarketRetrievalError(Exception):
    """Raised when Kalshi markets cannot be retrieved or converted."""


def get_active_markets(
    client: KalshiClient,
    limit: int = 100,
    max_pages: int | None = None,
) -> list[Market]:
    markets: list[Market] = []
    cursor: str | None = None
    seen_cursors: set[str] = set()
    page = 0

    while True:
        page += 1

        params: dict[str, str | int] = {
            "status": "open",
            "limit": limit,
        }

        if cursor:
            params["cursor"] = cursor

        response = client.get(
            "/markets",
            params=params,
        )

        raw_markets = response.get("markets", [])

        try:
            markets.extend(Market.from_kalshi(raw_market) for raw_market in raw_markets)
        except (ValueError, TypeError, KeyError) as exc:
            raise MarketRetrievalError("Unable to convert Kalshi market response.") from exc

        next_cursor = response.get("cursor")

        if not next_cursor:
            break

        if next_cursor in seen_cursors:
            raise MarketRetrievalError(
                "Kalshi pagination cursor repeated. Aborting to prevent an infinite loop."
            )

        seen_cursors.add(next_cursor)
        cursor = next_cursor

        if max_pages is not None and page >= max_pages:
            break

    return markets

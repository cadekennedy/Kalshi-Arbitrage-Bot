from datetime import datetime
from decimal import Decimal

import pytest

from app.models.market import Market, MarketDataError


def test_market_from_kalshi():
    raw_market = {
        "ticker": "TEST-MARKET",
        "event_ticker": "TEST-EVENT",
        "title": "Will the test pass?",
        "status": "active",
        "open_time": "2026-10-13T12:00:00Z",
        "close_time": "2026-10-14T12:00:00Z",
        "yes_bid_dollars": "0.4500",
        "yes_ask_dollars": "0.4700",
        "no_bid_dollars": "0.5300",
        "no_ask_dollars": "0.5500",
        "last_price_dollars": "0.4600",
        "volume_fp": "1234.00",
        "open_interest_fp": "500.00",
    }

    market = Market.from_kalshi(raw_market)

    assert market.ticker == "TEST-MARKET"
    assert market.event_ticker == "TEST-EVENT"
    assert market.title == "Will the test pass?"
    assert market.status == "active"

    assert market.yes_bid == Decimal("0.4500")
    assert market.yes_ask == Decimal("0.4700")
    assert market.no_bid == Decimal("0.5300")
    assert market.no_ask == Decimal("0.5500")

    assert market.last_price == Decimal("0.4600")

    assert market.volume == Decimal("1234.00")
    assert market.open_interest == Decimal("500.00")

    assert isinstance(market.open_time, datetime)
    assert isinstance(market.close_time, datetime)


def test_market_allows_missing_optional_prices():
    raw_market = {
        "ticker": "EMPTY-BOOK",
        "title": "Empty market",
        "status": "active",
    }

    market = Market.from_kalshi(raw_market)

    assert market.yes_bid is None
    assert market.yes_ask is None
    assert market.no_bid is None
    assert market.no_ask is None


def test_market_missing_ticker_raises_error():
    raw_market = {
        "title": "Missing ticker",
        "status": "active",
    }

    with pytest.raises(MarketDataError):
        Market.from_kalshi(raw_market)


def test_market_missing_title_raises_error():
    raw_market = {
        "ticker": "TEST",
        "status": "active",
    }

    with pytest.raises(MarketDataError):
        Market.from_kalshi(raw_market)


def test_market_missing_status_raises_error():
    raw_market = {
        "ticker": "TEST",
        "title": "Test market",
    }

    with pytest.raises(MarketDataError):
        Market.from_kalshi(raw_market)

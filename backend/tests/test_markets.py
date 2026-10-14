from unittest.mock import Mock

import pytest

from app.market_data.markets import (
    MarketRetrievalError,
    get_active_markets,
)


def make_market(ticker: str) -> dict:
    return {
        "ticker": ticker,
        "event_ticker": "TEST-EVENT",
        "title": f"Market {ticker}",
        "status": "open",
        "yes_bid_dollars": "0.4500",
        "yes_ask_dollars": "0.4700",
        "no_bid_dollars": "0.5300",
        "no_ask_dollars": "0.5500",
        "last_price_dollars": "0.4600",
        "volume_fp": "100.00",
        "open_interest_fp": "50.00",
    }


def test_get_active_markets_single_page():
    client = Mock()

    client.get.return_value = {
        "markets": [
            make_market("TEST-1"),
            make_market("TEST-2"),
        ],
        "cursor": "",
    }

    markets = get_active_markets(client)

    assert len(markets) == 2
    assert markets[0].ticker == "TEST-1"
    assert markets[1].ticker == "TEST-2"

    client.get.assert_called_once_with(
        "/markets",
        params={
            "status": "open",
            "limit": 100,
        },
    )


def test_get_active_markets_handles_pagination():
    client = Mock()

    client.get.side_effect = [
        {
            "markets": [
                make_market("TEST-1"),
            ],
            "cursor": "next-page",
        },
        {
            "markets": [
                make_market("TEST-2"),
            ],
            "cursor": "",
        },
    ]

    markets = get_active_markets(client)

    assert len(markets) == 2
    assert markets[0].ticker == "TEST-1"
    assert markets[1].ticker == "TEST-2"

    assert client.get.call_count == 2

    first_call = client.get.call_args_list[0]
    second_call = client.get.call_args_list[1]

    assert first_call.kwargs["params"] == {
        "status": "open",
        "limit": 100,
    }

    assert second_call.kwargs["params"] == {
        "status": "open",
        "limit": 100,
        "cursor": "next-page",
    }


def test_get_active_markets_empty_response():
    client = Mock()

    client.get.return_value = {
        "markets": [],
        "cursor": "",
    }

    markets = get_active_markets(client)

    assert markets == []


def test_get_active_markets_detects_repeated_cursor():
    client = Mock()

    client.get.side_effect = [
        {
            "markets": [
                make_market("TEST-1"),
            ],
            "cursor": "same-cursor",
        },
        {
            "markets": [
                make_market("TEST-2"),
            ],
            "cursor": "same-cursor",
        },
    ]

    with pytest.raises(MarketRetrievalError):
        get_active_markets(client)


def test_get_active_markets_respects_max_pages():
    client = Mock()

    client.get.side_effect = [
        {
            "markets": [
                make_market("TEST-1"),
            ],
            "cursor": "page-2",
        },
        {
            "markets": [
                make_market("TEST-2"),
            ],
            "cursor": "page-3",
        },
        {
            "markets": [
                make_market("TEST-3"),
            ],
            "cursor": "page-4",
        },
    ]

    markets = get_active_markets(
        client,
        max_pages=2,
    )

    assert len(markets) == 2
    assert markets[0].ticker == "TEST-1"
    assert markets[1].ticker == "TEST-2"
    assert client.get.call_count == 2

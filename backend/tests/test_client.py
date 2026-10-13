from unittest.mock import Mock, patch

import pytest

from app.market_data.client import KalshiAPIError, KalshiClient


def test_get_returns_json():
    auth = Mock()
    auth.headers.return_value = {
        "KALSHI-ACCESS-KEY": "test",
        "KALSHI-ACCESS-TIMESTAMP": "123",
        "KALSHI-ACCESS-SIGNATURE": "signature",
    }

    client = KalshiClient(
        base_url="https://example.com/trade-api/v2",
        auth=auth,
    )

    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"status": "ok"}

    with patch(
        "app.market_data.client.requests.get",
        return_value=mock_response,
    ) as mock_get:
        result = client.get("/portfolio/balance")

    assert result == {"status": "ok"}

    auth.headers.assert_called_once_with(
        method="GET",
        path="/trade-api/v2/portfolio/balance",
    )

    mock_get.assert_called_once()


def test_get_passes_query_params():
    auth = Mock()
    auth.headers.return_value = {}

    client = KalshiClient(
        base_url="https://example.com/trade-api/v2",
        auth=auth,
    )

    mock_response = Mock()
    mock_response.ok = True
    mock_response.json.return_value = {"markets": []}

    with patch(
        "app.market_data.client.requests.get",
        return_value=mock_response,
    ) as mock_get:
        client.get(
            "/markets",
            params={"limit": 100},
        )

    _, kwargs = mock_get.call_args

    assert kwargs["params"] == {"limit": 100}


def test_get_raises_api_error():
    auth = Mock()
    auth.headers.return_value = {}

    client = KalshiClient(
        base_url="https://example.com/trade-api/v2",
        auth=auth,
    )

    mock_response = Mock()
    mock_response.ok = False
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch(
        "app.market_data.client.requests.get",
        return_value=mock_response,
    ):
        with pytest.raises(KalshiAPIError):
            client.get("/portfolio/balance")

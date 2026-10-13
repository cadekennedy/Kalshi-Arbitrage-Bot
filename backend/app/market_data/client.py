import requests

from app.market_data.auth import KalshiAuth


class KalshiAPIError(Exception):
    """Raised when a Kalshi API request fails."""


class KalshiClient:
    def __init__(
        self,
        base_url: str = "https://api.elections.kalshi.com/trade-api/v2",
        timeout: int = 10,
        auth: KalshiAuth | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth = auth or KalshiAuth.from_settings()

    def get(
        self,
        path: str,
        params: dict | None = None,
    ) -> dict:
        normalized_path = path if path.startswith("/") else f"/{path}"

        signing_path = f"/trade-api/v2{normalized_path}"

        headers = self.auth.headers(
            method="GET",
            path=signing_path,
        )

        response = requests.get(
            f"{self.base_url}{normalized_path}",
            headers=headers,
            params=params,
            timeout=self.timeout,
        )

        if not response.ok:
            raise KalshiAPIError(
                f"Kalshi API request failed with status {response.status_code}: {response.text}"
            )

        return response.json()

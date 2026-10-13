import requests

from app.market_data.auth import KalshiAuth

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
PATH = "/portfolio/balance"


def main():
    auth = KalshiAuth.from_settings()

    headers = auth.headers(
        method="GET",
        path=f"/trade-api/v2{PATH}",
    )

    response = requests.get(
        f"{BASE_URL}{PATH}",
        headers=headers,
        timeout=10,
    )

    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    main()

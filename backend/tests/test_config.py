from app.config import settings


def test_default_trading_mode():

    assert settings.trading_mode == "paper"

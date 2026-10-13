import base64
import time
from pathlib import Path
from urllib.parse import urlsplit

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

from app.config import settings


class KalshiAuthenticationError(Exception):
    """Raised when Kalshi authentication cannot be configured or performed."""


class KalshiAuth:
    def __init__(
        self,
        key_id: str,
        private_key_path: str,
    ):
        if not key_id:
            raise KalshiAuthenticationError("Kalshi API key ID is missing.")

        if not private_key_path:
            raise KalshiAuthenticationError("Kalshi private key path is missing.")

        self.key_id = key_id
        self.private_key_path = Path(private_key_path).expanduser()
        self.private_key = self._load_private_key()

    @classmethod
    def from_settings(cls):
        return cls(
            key_id=settings.kalshi_api_key_id,
            private_key_path=settings.kalshi_private_key_path,
        )

    def _load_private_key(self):
        if not self.private_key_path.exists():
            raise KalshiAuthenticationError(
                f"Kalshi private key file was not found: {self.private_key_path}"
            )

        try:
            private_key_bytes = self.private_key_path.read_bytes()

            return serialization.load_pem_private_key(
                private_key_bytes,
                password=None,
            )

        except (ValueError, TypeError) as exc:
            raise KalshiAuthenticationError(
                "Unable to load Kalshi private key."
            ) from exc

    @staticmethod
    def _normalize_path(path: str) -> str:
        parsed = urlsplit(path)

        if parsed.scheme:
            normalized = parsed.path
        else:
            normalized = path.split("?", 1)[0]

        if not normalized.startswith("/"):
            normalized = f"/{normalized}"

        return normalized

    def sign(
        self,
        method: str,
        path: str,
        timestamp_ms: int,
    ) -> str:
        normalized_path = self._normalize_path(path)

        message = (
            f"{timestamp_ms}{method.upper()}{normalized_path}"
        ).encode("utf-8")

        if isinstance(self.private_key, ed25519.Ed25519PrivateKey):
            signature = self.private_key.sign(message)

        elif isinstance(self.private_key, rsa.RSAPrivateKey):
            signature = self.private_key.sign(
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=hashes.SHA256().digest_size,
                ),
                hashes.SHA256(),
            )

        else:
            raise KalshiAuthenticationError(
                "Unsupported Kalshi private key type."
            )

        return base64.b64encode(signature).decode("utf-8")

    def headers(
        self,
        method: str,
        path: str,
        timestamp_ms: int | None = None,
    ) -> dict[str, str]:
        if timestamp_ms is None:
            timestamp_ms = int(time.time() * 1000)

        signature = self.sign(
            method=method,
            path=path,
            timestamp_ms=timestamp_ms,
        )

        return {
            "KALSHI-ACCESS-KEY": self.key_id,
            "KALSHI-ACCESS-TIMESTAMP": str(timestamp_ms),
            "KALSHI-ACCESS-SIGNATURE": signature,
        }
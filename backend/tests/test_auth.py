import base64

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ed25519, padding, rsa

from app.market_data.auth import KalshiAuth, KalshiAuthenticationError


def write_private_key(tmp_path, private_key):
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    key_path = tmp_path / "kalshi_private_key.pem"
    key_path.write_bytes(pem)

    return key_path


def test_missing_key_id_raises_error(tmp_path):
    private_key = ed25519.Ed25519PrivateKey.generate()
    key_path = write_private_key(tmp_path, private_key)

    with pytest.raises(KalshiAuthenticationError):
        KalshiAuth(
            key_id="",
            private_key_path=str(key_path),
        )


def test_missing_private_key_path_raises_error():
    with pytest.raises(KalshiAuthenticationError):
        KalshiAuth(
            key_id="test-key",
            private_key_path="",
        )


def test_nonexistent_private_key_raises_error():
    with pytest.raises(KalshiAuthenticationError):
        KalshiAuth(
            key_id="test-key",
            private_key_path="/does/not/exist.pem",
        )


def test_ed25519_headers_are_generated(tmp_path):
    private_key = ed25519.Ed25519PrivateKey.generate()
    key_path = write_private_key(tmp_path, private_key)

    auth = KalshiAuth(
        key_id="test-key",
        private_key_path=str(key_path),
    )

    headers = auth.headers(
        method="GET",
        path="/trade-api/v2/portfolio/balance",
        timestamp_ms=1234567890000,
    )

    assert headers["KALSHI-ACCESS-KEY"] == "test-key"
    assert headers["KALSHI-ACCESS-TIMESTAMP"] == "1234567890000"
    assert headers["KALSHI-ACCESS-SIGNATURE"]


def test_ed25519_signature_is_valid(tmp_path):
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    key_path = write_private_key(tmp_path, private_key)

    auth = KalshiAuth(
        key_id="test-key",
        private_key_path=str(key_path),
    )

    timestamp = 1234567890000
    path = "/trade-api/v2/portfolio/balance"

    encoded_signature = auth.sign(
        method="GET",
        path=path,
        timestamp_ms=timestamp,
    )

    signature = base64.b64decode(encoded_signature)

    message = f"{timestamp}GET{path}".encode()

    public_key.verify(signature, message)


def test_query_parameters_are_not_signed(tmp_path):
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    key_path = write_private_key(tmp_path, private_key)

    auth = KalshiAuth(
        key_id="test-key",
        private_key_path=str(key_path),
    )

    timestamp = 1234567890000

    signature = base64.b64decode(
        auth.sign(
            method="GET",
            path="/trade-api/v2/markets?limit=100",
            timestamp_ms=timestamp,
        )
    )

    message = (f"{timestamp}GET/trade-api/v2/markets").encode()

    public_key.verify(signature, message)


def test_rsa_signature_is_valid(tmp_path):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    public_key = private_key.public_key()
    key_path = write_private_key(tmp_path, private_key)

    auth = KalshiAuth(
        key_id="test-key",
        private_key_path=str(key_path),
    )

    timestamp = 1234567890000
    path = "/trade-api/v2/portfolio/balance"

    signature = base64.b64decode(
        auth.sign(
            method="GET",
            path=path,
            timestamp_ms=timestamp,
        )
    )

    message = f"{timestamp}GET{path}".encode()

    public_key.verify(
        signature,
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=hashes.SHA256().digest_size,
        ),
        hashes.SHA256(),
    )

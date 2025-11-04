"""Unit tests for webhook signature verification."""

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_sendgrid_signature():
    """Mock SendGrid signature verification."""
    # Sample public key (this is a dummy key for testing)
    public_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE83T4O/n84iotIvIW4mdBgQ/7dAfS
mpqIM8kF/mTspKRaWkuMm1X/X2Z0jxZvZ8b7JhGvGMzLaJgDpLjMqvNL7w==
-----END PUBLIC KEY-----"""
    return public_key


def test_webhook_without_signature_when_no_public_key_configured():
    """Test webhook accepts requests when public key is not configured (dev mode)."""
    with patch.dict(os.environ, {"SENDGRID_WEBHOOK_PUBLIC_KEY": ""}, clear=False):
        response = client.post(
            "/api/webhooks/sendgrid",
            json=[
                {
                    "event": "delivered",
                    "invitation_id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "test@example.com",
                }
            ],
        )
        # Should accept webhook in dev mode but invitation won't be found
        assert response.status_code in [200, 404]  # 200 if processed, 404 if not found


def test_webhook_rejects_request_without_signature_headers_when_key_configured(
    mock_sendgrid_signature,
):
    """Test webhook rejects requests missing signature headers when public key is configured."""
    with patch.dict(
        os.environ,
        {"SENDGRID_WEBHOOK_PUBLIC_KEY": mock_sendgrid_signature},
        clear=False,
    ):
        response = client.post(
            "/api/webhooks/sendgrid",
            json=[{"event": "delivered"}],
        )
        assert response.status_code == 403
        assert "Missing required signature headers" in response.json()["detail"]


def test_webhook_rejects_request_with_invalid_signature(mock_sendgrid_signature):
    """Test webhook rejects requests with invalid signature."""
    with patch.dict(
        os.environ,
        {"SENDGRID_WEBHOOK_PUBLIC_KEY": mock_sendgrid_signature},
        clear=False,
    ):
        response = client.post(
            "/api/webhooks/sendgrid",
            json=[{"event": "delivered"}],
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": "invalid_signature",
                "X-Twilio-Email-Event-Webhook-Timestamp": "1234567890",
            },
        )
        assert response.status_code == 403
        assert "Invalid webhook signature" in response.json()["detail"]


def test_webhook_accepts_request_with_valid_signature(mock_sendgrid_signature):
    """Test webhook accepts requests with valid signature."""
    # This test would require generating a real valid signature
    # For now, we'll test the flow with mocked verification
    with patch.dict(
        os.environ,
        {"SENDGRID_WEBHOOK_PUBLIC_KEY": mock_sendgrid_signature},
        clear=False,
    ):
        with patch(
            "app.api.webhooks._verify_sendgrid_signature",
            return_value=True,
        ):
            response = client.post(
                "/api/webhooks/sendgrid",
                json=[
                    {
                        "event": "delivered",
                        "invitation_id": "123e4567-e89b-12d3-a456-426614174000",
                    }
                ],
                headers={
                    "X-Twilio-Email-Event-Webhook-Signature": "valid_signature",
                    "X-Twilio-Email-Event-Webhook-Timestamp": "1234567890",
                },
            )
            # Should accept the request (invitation might not be found, that's OK)
            assert response.status_code == 200
            assert response.json()["status"] == "success"


def test_webhook_rejects_invalid_json():
    """Test webhook rejects requests with invalid JSON."""
    with patch.dict(os.environ, {"SENDGRID_WEBHOOK_PUBLIC_KEY": ""}, clear=False):
        response = client.post(
            "/api/webhooks/sendgrid",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400
        assert "Invalid JSON payload" in response.json()["detail"]


def test_signature_verification_error_handling(mock_sendgrid_signature):
    """Test signature verification handles exceptions gracefully."""
    with patch.dict(
        os.environ,
        {"SENDGRID_WEBHOOK_PUBLIC_KEY": "invalid_key_format"},
        clear=False,
    ):
        response = client.post(
            "/api/webhooks/sendgrid",
            json=[{"event": "delivered"}],
            headers={
                "X-Twilio-Email-Event-Webhook-Signature": "signature",
                "X-Twilio-Email-Event-Webhook-Timestamp": "1234567890",
            },
        )
        # Should return 403 because verification fails due to invalid key
        assert response.status_code == 403

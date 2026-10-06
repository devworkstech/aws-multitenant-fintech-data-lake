import json
import pytest
from src.ingestion.handler import handler, validate_event

EVENT = {
    "tenant_id": "bank-demo-01",
    "account_id": "acct-1001",
    "event_type": "payment",
    "amount": "42.50",
    "event_time": "2026-10-01T12:00:00Z",
    "currency": "USD",
}


def test_valid_event_has_tenant_partition():
    response = handler(EVENT)
    body = json.loads(response["body"])
    assert response["statusCode"] == 202
    assert "tenant_id=bank-demo-01" in body["s3_key"]
    assert body["record"]["amount"] == "42.50"


def test_rejects_negative_amount():
    bad = dict(EVENT, amount="-1")
    with pytest.raises(ValueError, match="positive"):
        validate_event(bad)


def test_rejects_unknown_event_type():
    bad = dict(EVENT, event_type="unknown")
    with pytest.raises(ValueError, match="unsupported"):
        validate_event(bad)

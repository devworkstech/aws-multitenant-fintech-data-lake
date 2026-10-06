"""Tenant-aware ingestion contract for synthetic financial events."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

ALLOWED_TYPES = {"payment", "deposit", "withdrawal", "transfer"}
REQUIRED = {"tenant_id", "account_id", "event_type", "amount", "event_time"}


def validate_event(event: dict) -> dict:
    missing = REQUIRED - event.keys()
    if missing:
        raise ValueError(f"missing required fields: {sorted(missing)}")
    if event["event_type"] not in ALLOWED_TYPES:
        raise ValueError("unsupported event_type")
    try:
        amount = Decimal(str(event["amount"]))
    except InvalidOperation as exc:
        raise ValueError("amount must be numeric") from exc
    if amount <= 0:
        raise ValueError("amount must be positive")
    timestamp = datetime.fromisoformat(event["event_time"].replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("event_time must include timezone")
    normalized = dict(event)
    normalized["amount"] = str(amount.quantize(Decimal("0.01")))
    normalized["event_time"] = timestamp.astimezone(timezone.utc).isoformat()
    return normalized


def event_id(event: dict) -> str:
    canonical = "|".join(
        str(event[k]) for k in ("tenant_id", "account_id", "event_type", "amount", "event_time")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def s3_key(event: dict) -> str:
    day = datetime.fromisoformat(event["event_time"]).date().isoformat()
    return f"raw/tenant_id={event['tenant_id']}/event_date={day}/{event_id(event)}.json"


def handler(event, context=None):
    """Validate an event and return its deterministic storage envelope.

    A production Lambda can pass this envelope to boto3.put_object. Keeping storage
    outside the contract makes validation deterministic and locally testable.
    """
    payload = event.get("body", event)
    if isinstance(payload, str):
        payload = json.loads(payload)
    record = validate_event(payload)
    return {
        "statusCode": 202,
        "body": json.dumps({"event_id": event_id(record), "s3_key": s3_key(record), "record": record}),
    }

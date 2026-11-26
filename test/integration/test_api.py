"""Local FastAPI service: status, uncertainty and evidence signals; invalid input rejected."""

import base64
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

from backend import main
from backend.main import MAX_IMAGE_B64_LENGTH, app
from conftest import SAMPLE_TEXT, make_image

client = TestClient(app)


def post(modality, payload):
    """Send one analyze request with a fresh request id."""
    return client.post(
        "/api/v1/analyze",
        json={"req_id": str(uuid.uuid4()), "modality": modality, "payload": payload},
    )


def test_healthz():
    """The health endpoint answers ok.

    Why: the demo and availability probes rely on it (NFR8).
    """
    assert client.get("/healthz").json() == {"status": "ok"}


@pytest.mark.parametrize(
    ("modality", "payload"),
    [("text", SAMPLE_TEXT), ("image", base64.b64encode(make_image("JPEG")).decode())],
)
def test_valid_check_returns_status_uncertainty_and_signals(modality, payload):
    """Valid text and images return inconclusive with uncertainty, evidence and next steps.

    Why: with no validated detector, the service must not give a direction (INV2, FR3-FR5).
    """
    r = post(modality, payload)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "inconclusive" and data["uncertainty"] and data["limitations"]
    assert data["verification_steps"]
    assert data["signals"] and all(s["source"] == "observed_signal" for s in data["signals"])


# Each row is (modality, payload, expected rejection code).
@pytest.mark.parametrize(
    ("modality", "payload", "code"),
    [
        ("text", "too short", "text_too_short"),
        ("image", base64.b64encode(make_image("PNG", (32, 32))).decode(), "image_too_small"),
        ("image", base64.b64encode(make_image("GIF")).decode(), "unsupported_format"),
        ("image", "not base64!", "corrupt_image"),
        # One character past the longest base64 encoding of a 10.0 MB image.
        ("image", "A" * (MAX_IMAGE_B64_LENGTH + 1), "image_too_large"),
    ],
)
def test_invalid_input_is_rejected(modality, payload, code):
    """Invalid input gets a 422 with the validation gate's rejection code.

    Why: the service must enforce FR2 itself, not trust the client.
    """
    r = post(modality, payload)
    assert r.status_code == 422 and r.json()["error"]["code"] == code


def test_malformed_request_does_not_echo_input():
    """A malformed request's error reply does not contain the submitted payload.

    Why: error messages must never leak user content (FR9).
    """
    r = client.post(
        "/api/v1/analyze", json={"req_id": "x", "modality": "text", "payload": "SECRET"}
    )
    assert r.status_code == 422 and "SECRET" not in r.text


def test_timeout_stops_worker_before_returning_failed(monkeypatch):
    """A stalled check releases its worker before the API reports a terminal result."""
    start_process = main.create_subprocess_exec
    workers = []

    async def start_stalled_worker(*_command, **options):
        worker = await start_process(
            sys.executable,
            "-c",
            "import sys, time; sys.stdin.buffer.read(); time.sleep(5)",
            **options,
        )
        workers.append(worker)
        return worker

    monkeypatch.setattr(main, "create_subprocess_exec", start_stalled_worker)
    monkeypatch.setattr(main, "MAX_RESPONSE_TIME", 0.5)

    with client:
        response = post("text", SAMPLE_TEXT)
        assert response.status_code == 200
        assert response.json()["status"] == "failed"
        assert "too long" in response.json()["uncertainty"]
        assert len(workers) == 1
        assert workers[0].returncode is not None

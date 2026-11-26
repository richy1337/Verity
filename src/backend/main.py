"""Local FastAPI analysis service for the POC demo.

No validated detector exists yet, so the service reports observed signals and
returns ``inconclusive``. It never gives a direction without a calibrated score (INV2).

Run locally: ``uv run uvicorn backend.main:app --port 8000``
"""

import asyncio
import base64
import binascii
import json
import re
import statistics
import sys
from asyncio import create_subprocess_exec
from contextlib import suppress
from typing import Literal
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, TypeAdapter

from backend.constants import (
    LIMIT_NO_GUARANTEE,
    MAX_CONCURRENT_REQS,
    MAX_IMAGE_SIZE,
    MAX_RESPONSE_TIME,
)
from backend.validation import Rejection, validate_image, validate_text

VERIFY_STEP = "Check the original source or ask its author before relying on this content."
# Base64 turns every 3 bytes into 4 characters, so this is the longest valid encoding.
MAX_IMAGE_B64_LENGTH = 4 * -(-MAX_IMAGE_SIZE // 3)


class AnalyzeRequest(BaseModel):
    """What the client sends. Extra fields (e.g. session_token) are accepted and ignored.

    Why: a typed request lets FastAPI reject malformed input before our code runs.
    """

    req_id: UUID
    modality: Literal["text", "image"]
    payload: str  # text, or base64 image bytes


class Signal(BaseModel):
    """One piece of evidence: where it came from, where it is, and what it says.

    Why: every displayed claim must be tagged with its source (FR7, SR5, H3).
    """

    signal_id: str
    source: Literal["observed_signal", "external_reference", "inference"]
    locator: str
    summary: str


class AnalyzeResponse(BaseModel):
    """What the service returns: status, uncertainty, evidence, limits and next steps.

    Why: matches the SRS S.5 result contract so the UI never shows a bare score (SR1, SR2).
    """

    req_id: UUID
    status: Literal["completed", "inconclusive", "failed"]
    summary_label: str
    uncertainty: str
    signals: list[Signal] = []
    limitations: list[str] = [LIMIT_NO_GUARANTEE]
    verification_steps: list[str] = [VERIFY_STEP]


_CHECK_RESULT = TypeAdapter(list[Signal] | Rejection)
_WORKER_SLOTS = asyncio.Semaphore(MAX_CONCURRENT_REQS)

app = FastAPI(title="Verity analysis service")


@app.exception_handler(RequestValidationError)
async def _malformed(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Reply to a malformed request with the bad field names only.

    Why: FastAPI's default reply echoes the submitted input back, which could leak content (FR9).
    """
    fields = sorted({str(e["loc"][-1]) for e in exc.errors()})
    return JSONResponse({"error": {"code": "malformed_request", "fields": fields}}, status_code=422)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    """Report that the service is up.

    Why: availability probes and the demo laptop can check the service is running (NFR8).
    """
    return {"status": "ok"}


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """Validate one selection, then return its signals; invalid input gets a 422 rejection.

    Why: this is the single entry point the extension and demo walkthrough call (UC1, UC3).
    """
    try:
        result = await _check_in_worker(req)
    except TimeoutError:
        return _failed(req.req_id, "The check took too long. No assessment was made.")
    except Exception:
        return _failed(req.req_id, "The analysis could not be completed.")
    # Invalid input is refused before analysis and never enters the lifecycle (FR2, INV1).
    if isinstance(result, Rejection):
        return JSONResponse(
            {"error": {"code": result.code, "message": result.message}}, status_code=422
        )
    return AnalyzeResponse(
        req_id=req.req_id,
        status="inconclusive",
        summary_label="Not enough reliable evidence to assess this selection",
        uncertainty="No validated detector is active yet, so no direction is given.",
        signals=result,
    )


async def _check_in_worker(req: AnalyzeRequest) -> list[Signal] | Rejection:
    """Run one check in a process that can be stopped at the response deadline."""
    async with asyncio.timeout(MAX_RESPONSE_TIME), _WORKER_SLOTS:
        # The payload travels over a private pipe, separate from the command line and logs.
        request = json.dumps(req.model_dump(mode="json")).encode("ascii")
        worker = await create_subprocess_exec(
            sys.executable,
            "-m",
            "backend.main",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        try:
            output, _ = await worker.communicate(request)
        finally:
            if worker.returncode is None:
                # A cancelled wait leaves the worker running. Stop it before returning a result.
                with suppress(ProcessLookupError):
                    worker.kill()
                await worker.wait()

    if worker.returncode != 0:
        raise RuntimeError("The analysis worker exited unexpectedly.")
    return _CHECK_RESULT.validate_json(output)


def _check(req: AnalyzeRequest) -> list[Signal] | Rejection:
    """Validate the payload and, if it passes, collect its observed signals.

    Why: a single worker owns validation and signal extraction for this selection.
    """
    if req.modality == "text":
        return validate_text(req.payload) or _text_signals(req.payload)
    # Images arrive as base64; accept an optional "data:image/...;base64," prefix.
    encoded = req.payload.split(",")[-1]
    # Refuse oversized payloads before decoding, so a huge upload costs no memory (H7).
    if len(encoded) > MAX_IMAGE_B64_LENGTH:
        return Rejection("image_too_large", "Images must be 10.0 MB or smaller.")
    try:
        data = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return Rejection("corrupt_image", "The image could not be read.")
    info = validate_image(data)
    if isinstance(info, Rejection):
        return info
    return [
        Signal(
            signal_id="image.container",
            source="observed_signal",
            locator="file header",
            summary=f"{info.format} image, {info.width}x{info.height} px.",
        ),
        Signal(
            signal_id="image.exif",
            source="observed_signal",
            locator="EXIF block",
            # Missing metadata is reported as missing provenance, not as manipulation.
            summary=(
                f"{info.exif_fields} camera metadata fields"
                if info.exif_fields
                else "No camera metadata (common after uploads; not evidence of generation)."
            ),
        ),
    ]


def _text_signals(text: str) -> list[Signal]:
    """Measure simple, explainable text statistics: word variety and sentence-length variation.

    Why: gives the user real observed evidence even before a trained detector exists (FR3).
    """
    loc = f"chars 0-{len(text)}"
    words = re.findall(r"\w+", text.casefold())
    lengths = [len(re.findall(r"\w+", s)) for s in re.split(r"[.!?]+", text) if s.strip()]
    signals = [
        Signal(
            signal_id="text.vocabulary_diversity",
            source="observed_signal",
            locator=loc,
            summary=f"{len(set(words)) / max(len(words), 1):.2f} of words are distinct.",
        )
    ]
    # Burstiness needs at least two sentences to compare.
    if len(lengths) >= 2:
        cv = statistics.pstdev(lengths) / statistics.fmean(lengths)
        signals.append(
            Signal(
                signal_id="text.burstiness",
                source="observed_signal",
                locator=loc,
                summary=f"Sentence length varies by {cv:.2f} (coefficient of variation).",
            )
        )
    return signals


def _failed(req_id: UUID, message: str) -> AnalyzeResponse:
    """Build a ``failed`` response with no signals.

    Why: a timeout or crash must show as failed, never as a safe result (FR6, SR4, H6).
    """
    return AnalyzeResponse(
        req_id=req_id,
        status="failed",
        summary_label="The check could not be completed",
        uncertainty=message,
    )


if __name__ == "__main__":
    # A worker handles one selection, then exits and releases its input.
    # Keep JSON escapes intact so the validator can reject text that cannot be encoded as UTF-8.
    request = AnalyzeRequest.model_validate(json.load(sys.stdin.buffer))
    sys.stdout.buffer.write(_CHECK_RESULT.dump_json(_check(request)))

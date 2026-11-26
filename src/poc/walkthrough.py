"""Show Verity PoC example responses or call the local analysis service."""

import argparse
import base64
import json
import sys
import time
from http.client import HTTPConnection, HTTPException
from pathlib import Path
from uuid import uuid4


HOST = "127.0.0.1"
DEFAULT_PORT = 8000
SOCKET_TIMEOUT_SECONDS = 12
ANALYZE_PATH = "/api/v1/analyze"
EVIDENCE_SOURCES = {
    "observed_signal": "Observed Input Signal",
    "external_reference": "External Reference",
    "inference": "Model Inference",
}
UNASSESSED_STATUSES = {
    "pending": "The service is still processing the request.",
    "failed": "The service did not complete the analysis.",
    "cancelled": "The analysis was cancelled.",
}


def submit(input_path, modality, port):
    if modality == "text":
        payload = input_path.read_bytes().decode("utf-8")
    else:
        payload = base64.b64encode(input_path.read_bytes()).decode("ascii")

    request_id = str(uuid4())
    request = {
        "req_id": request_id,
        "session_token": str(uuid4()),
        "modality": modality,
        "payload": payload,
        "source_origin": f"http://{HOST}:{port}",
        "consent_granted": False,
        "client_timestamp_ms": time.time_ns() // 1_000_000,
    }
    connection = HTTPConnection(HOST, port, timeout=SOCKET_TIMEOUT_SECONDS)
    try:
        connection.request(
            "POST",
            ANALYZE_PATH,
            body=json.dumps(request).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with connection.getresponse() as response:
            if not 200 <= response.status < 300:
                raise ValueError(f"Analysis endpoint returned HTTP {response.status}.")
            result = json.load(response)
    finally:
        connection.close()

    if not isinstance(result, dict) or result.get("req_id") != request_id:
        raise ValueError("The response did not match this request.")
    return result


def display_text(value, field):
    if not isinstance(value, str):
        raise ValueError(f"The response is missing readable {field}.")
    text = "".join(char if char.isprintable() else " " for char in value).strip()
    if not text:
        raise ValueError(f"The response is missing readable {field}.")
    return text


def result_lines(result):
    status = result.get("status")
    if not isinstance(status, str):
        raise ValueError("The response has no recognized analysis status.")
    if status in UNASSESSED_STATUSES:
        return [f"Status  {status}", UNASSESSED_STATUSES[status]]
    if status not in {"completed", "inconclusive"}:
        raise ValueError("The response has no recognized analysis status.")

    lines = [f"Status  {status}"]
    if status == "completed":
        lines.append(display_text(result.get("summary_label"), "assessment summary"))
        warning = result.get("false_positive_warning")
        if warning is not None:
            lines.append(display_text(warning, "false-positive warning"))
    uncertainty = display_text(result.get("uncertainty"), "uncertainty")
    lines.extend(["", "Uncertainty", uncertainty])

    signals = result.get("signals")
    if not isinstance(signals, list) or (status == "completed" and not signals):
        raise ValueError("The response is missing required evidence.")
    lines.extend(["", "Evidence"])
    for signal in signals:
        source = signal.get("source") if isinstance(signal, dict) else None
        if not isinstance(source, str) or source not in EVIDENCE_SOURCES:
            raise ValueError("The response contains evidence with an unknown source.")
        summary = display_text(signal.get("summary"), "evidence summary")
        locator = display_text(signal.get("locator"), "evidence locator")
        lines.append(f"- [{EVIDENCE_SOURCES[source]}] {summary} ({locator})")
    if not signals:
        lines.append("The service returned no supporting evidence.")

    limitations = result.get("limitations")
    steps = result.get("verification_steps")
    if not isinstance(limitations, list) or (status == "completed" and not limitations):
        raise ValueError("The response is missing required limitations.")
    if not isinstance(steps, list) or not steps:
        raise ValueError("The response is missing verification guidance.")
    if limitations:
        lines.extend(["", "Limitations"])
        lines.extend(f"- {display_text(item, 'limitation')}" for item in limitations)
    lines.extend(["", "Next verification step"])
    lines.append(display_text(steps[0], "verification step"))
    lines.append("")
    lines.append("Independent evidence is required to establish authenticity or fraud.")
    return lines


def example_results(sample):
    examples = json.loads(sample.read_bytes())
    if not isinstance(examples, list) or not examples:
        raise ValueError("The example file must contain a list of responses.")
    for example in examples:
        response = example.get("response") if isinstance(example, dict) else None
        if not isinstance(response, dict):
            raise ValueError("The example file contains an invalid response.")
        title = display_text(example.get("title"), "example title")
        yield f"Verity PoC | Example response | {title}", result_lines(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("examples", "text", "image"))
    parser.add_argument("sample", type=Path, help="Example JSON, text, or image file")
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Local FastAPI port (default %(default)s)",
    )
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")

    try:
        if args.mode == "examples":
            displays = list(example_results(args.sample))
            exit_code = 0
        else:
            result = submit(args.sample, args.mode, args.port)
            title = f"Verity PoC | {args.mode.capitalize()} assessment"
            displays = [(title, result_lines(result))]
            exit_code = 0 if result["status"] in {"completed", "inconclusive"} else 1
    except UnicodeError:
        print("Invalid text encoding in sample or response.", file=sys.stderr)
    except json.JSONDecodeError:
        print("Invalid JSON in the example file or service response.", file=sys.stderr)
    except ValueError as error:
        print(error, file=sys.stderr)
    except TimeoutError:
        print("The local analysis service timed out.", file=sys.stderr)
    except OSError as error:
        if error.filename is None:
            print(f"Could not reach service on {HOST}:{args.port}.", file=sys.stderr)
        else:
            print(f"Could not read the sample file: {error.strerror}", file=sys.stderr)
    except HTTPException:
        print("The service returned an invalid HTTP response.", file=sys.stderr)
    else:
        blocks = (f"{title}\n\n" + "\n".join(lines) for title, lines in displays)
        print("\n\n".join(blocks))
        return exit_code
    return 1


if __name__ == "__main__":
    sys.exit(main())

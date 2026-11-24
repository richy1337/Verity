"""Thresholds from SRS Table 6 and MIS TblConstants. Import these; never hardcode them."""

from typing import Final

# Input validation bounds (M4; SRS Table 6 / MIS TblConstants)
MIN_TEXT_LENGTH: Final[int] = 150  # Unicode code points, inclusive
MAX_TEXT_LENGTH: Final[int] = 10_000  # Unicode code points, inclusive
MAX_IMAGE_SIZE: Final[int] = 10_000_000  # bytes (10.0 MB decimal)
MIN_IMAGE_DIM: Final[int] = 64  # pixels per axis, inclusive
MAX_IMAGE_DIM: Final[int] = 4096  # pixels per axis, inclusive

# Service coordination, lifecycle and ephemeral cleanup bounds (M5, M6)
MAX_RESPONSE_TIME: Final[float] = 10.0  # seconds from service admission
MAX_RESPONSE_TIME_S: Final[float] = MAX_RESPONSE_TIME
MAX_CONCURRENT_REQS: Final[int] = 10  # isolated admitted requests
MAX_DELIVERY_RECORD_AGE: Final[int] = 60  # seconds after terminal decision (MIS design bound)
MAX_DELIVERY_RECORD_AGE_S: Final[int] = MAX_DELIVERY_RECORD_AGE
MAX_RETENTION_TIME: Final[float] = 1.0  # seconds after local terminal decision
MAX_RETENTION_TIME_S: Final[float] = MAX_RETENTION_TIME

# Extension UI latency bounds (M1, M3)
MAX_UI_RENDER_LATENCY: Final[int] = 500  # milliseconds
MAX_UI_RENDER_LATENCY_MS: Final[int] = MAX_UI_RENDER_LATENCY
MAX_CANCEL_UI_LATENCY: Final[int] = 200  # milliseconds
MAX_CANCEL_UI_LATENCY_MS: Final[int] = MAX_CANCEL_UI_LATENCY

# Offline evaluation gates and reproducibility tolerance (M10)
MIN_F1_SCORE: Final[float] = 0.80
MIN_COVERAGE: Final[float] = 0.70
MAX_FPR: Final[float] = 0.10
MIN_BASELINE_DELTA: Final[float] = 0.10
MAX_REPRO_DELTA: Final[float] = 0.005

# Mandatory non-guarantee notice (M9; SRS FR5/SR3)
LIMIT_NO_GUARANTEE: Final[str] = "This assessment does not guarantee authenticity or prove fraud."

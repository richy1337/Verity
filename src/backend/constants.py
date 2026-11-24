"""Thresholds from SRS Table 6 / MIS TblConstants. Import these; never hardcode them."""

MIN_TEXT_LENGTH = 150  # Unicode code points, inclusive
MAX_TEXT_LENGTH = 10_000
MAX_IMAGE_SIZE = 10_000_000  # bytes (10.0 MB)
MIN_IMAGE_DIM = 64  # pixels per axis, inclusive
MAX_IMAGE_DIM = 4096
MAX_RESPONSE_TIME_S = 10.0

MIN_F1_SCORE = 0.80
MIN_COVERAGE = 0.70
MAX_FPR = 0.10
MIN_BASELINE_DELTA = 0.10

LIMIT_NO_GUARANTEE = "This assessment does not guarantee authenticity or prove fraud."

"""Code thresholds must match SRS Table 6 (TblSymbolicConstants) and MIS TblConstants."""

from backend import constants as c


def test_constants_match_srs_and_mis() -> None:
    assert (c.MIN_TEXT_LENGTH, c.MAX_TEXT_LENGTH) == (150, 10_000)
    assert c.MAX_IMAGE_SIZE == 10_000_000  # 10.0 MB, decimal
    assert (c.MIN_IMAGE_DIM, c.MAX_IMAGE_DIM) == (64, 4096)

    assert c.MAX_RESPONSE_TIME == c.MAX_RESPONSE_TIME_S == 10.0
    assert c.MAX_CONCURRENT_REQS == 10
    assert c.MAX_DELIVERY_RECORD_AGE == c.MAX_DELIVERY_RECORD_AGE_S == 60
    assert c.MAX_RETENTION_TIME == c.MAX_RETENTION_TIME_S == 1.0
    assert c.MAX_UI_RENDER_LATENCY == c.MAX_UI_RENDER_LATENCY_MS == 500
    assert c.MAX_CANCEL_UI_LATENCY == c.MAX_CANCEL_UI_LATENCY_MS == 200

    assert (c.MIN_F1_SCORE, c.MIN_COVERAGE, c.MAX_FPR) == (0.80, 0.70, 0.10)
    assert (c.MIN_BASELINE_DELTA, c.MAX_REPRO_DELTA) == (0.10, 0.005)
    assert c.LIMIT_NO_GUARANTEE == "This assessment does not guarantee authenticity or prove fraud."

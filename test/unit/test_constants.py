"""Code thresholds must match SRS Table 6 (TblSymbolicConstants)."""

from backend import constants as c


def test_constants_match_srs_table_6():
    assert (c.MIN_TEXT_LENGTH, c.MAX_TEXT_LENGTH) == (150, 10_000)
    assert c.MAX_IMAGE_SIZE == 10_000_000  # 10.0 MB, decimal
    assert (c.MIN_IMAGE_DIM, c.MAX_IMAGE_DIM) == (64, 4096)
    assert c.MAX_RESPONSE_TIME_S == 10.0
    assert (c.MIN_F1_SCORE, c.MIN_COVERAGE, c.MAX_FPR) == (0.80, 0.70, 0.10)
    assert c.MIN_BASELINE_DELTA == 0.10

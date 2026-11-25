"""M4 validation gate boundaries (FR2)."""

import pytest

from backend.constants import MAX_IMAGE_SIZE, MAX_TEXT_LENGTH, MIN_TEXT_LENGTH
from backend.validation import ImageInfo, Rejection, validate_image, validate_text
from conftest import make_image


# Each row is (input text, expected rejection code); None means the text is accepted.
@pytest.mark.parametrize(
    ("text", "code"),
    [
        ("", "empty_input"),
        ("   \n ", "empty_input"),
        ("a" * (MIN_TEXT_LENGTH - 1), "text_too_short"),
        ("a" * MIN_TEXT_LENGTH, None),
        ("a" * MAX_TEXT_LENGTH, None),
        ("a" * (MAX_TEXT_LENGTH + 1), "text_too_long"),
        ("\U0001f600" * MIN_TEXT_LENGTH, None),  # counts code points, not bytes
    ],
)
def test_text_bounds(text, code):
    """Text just inside each bound passes; one character outside is rejected.

    Why: off-by-one errors at 150 and 10,000 characters are the most likely bug (Class 5).
    """
    result = validate_text(text)
    assert (result.code if result else None) == code


@pytest.mark.parametrize("fmt", ["PNG", "JPEG", "WEBP"])
def test_supported_images_pass(fmt):
    """A normal image in each supported format is accepted with the right details.

    Why: the gate must not block valid input (Class 2).
    """
    assert validate_image(make_image(fmt)) == ImageInfo(fmt, 128, 96, 0)


# Each row is (image bytes, expected rejection code).
@pytest.mark.parametrize(
    ("data", "code"),
    [
        (make_image("PNG", (63, 64)), "image_too_small"),
        (make_image("PNG", (32, 32)), "image_too_small"),
        (make_image("PNG", (4097, 64)), "image_too_big"),
        (make_image("GIF"), "unsupported_format"),
        (b"<svg><script>alert(1)</script></svg>", "unsupported_format"),
        (b"\x89PNG\r\n\x1a\n" + b"\x00" * MAX_IMAGE_SIZE, "image_too_large"),
        (make_image("PNG", (256, 256))[:200], "corrupt_image"),
    ],
)
def test_ineligible_images_are_rejected(data, code):
    """Too small, too big, wrong format, script, oversized and truncated files are refused.

    Why: each one is a way untrusted webpage content could break or abuse the service
    (Classes 5 and 6, SR6, H7).
    """
    result = validate_image(data)
    assert isinstance(result, Rejection) and result.code == code


def test_minimum_image_size_is_inclusive():
    """Exactly 64x64 is accepted.

    Why: the SRS says the minimum is inclusive, so 64 must pass and 63 must fail.
    """
    assert isinstance(validate_image(make_image("PNG", (64, 64))), ImageInfo)

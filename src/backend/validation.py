"""M4 input validation gate (FR2): admit bounded text or static PNG/JPEG/WebP images.

Every selection passes through here before any analysis runs. Anything out of bounds,
unsupported or broken is rejected up front with a safe, user-readable reason.
"""

import io
import warnings
from dataclasses import dataclass

from PIL import Image

from backend.constants import (
    MAX_IMAGE_DIM,
    MAX_IMAGE_SIZE,
    MAX_TEXT_LENGTH,
    MIN_IMAGE_DIM,
    MIN_TEXT_LENGTH,
)


@dataclass(frozen=True)
class Rejection:
    """Why an input was refused: a machine ``code`` plus a plain-language ``message``.

    Why: the UI can explain the refusal without echoing the user's content back (FR9).
    """

    code: str
    message: str


@dataclass(frozen=True)
class ImageInfo:
    """Facts about an accepted image: format, size and number of EXIF fields.

    Why: later stages (image signals, provenance) reuse these instead of re-reading the file.
    """

    format: str
    width: int
    height: int
    exif_fields: int


def validate_text(text: str) -> Rejection | None:
    """Return a Rejection if the text is empty, too short or too long; otherwise None.

    Why: very short text gives unreliable signals (H2) and very long text costs too much (H7).
    """
    # Whitespace-only selections count as empty.
    if not text.strip():
        return Rejection("empty_input", "The selection is empty.")
    # len() counts characters (code points), so an emoji counts as 1, not 4 bytes.
    n = len(text)
    if n < MIN_TEXT_LENGTH:
        return Rejection("text_too_short", f"Select at least {MIN_TEXT_LENGTH} characters.")
    if n > MAX_TEXT_LENGTH:
        return Rejection("text_too_long", f"Select at most {MAX_TEXT_LENGTH:,} characters.")
    return None


def _sniff(data: bytes) -> str | None:
    """Identify PNG, JPEG or WebP from the file's first bytes ("magic bytes"); else None.

    Why: file names and declared types can lie; the bytes themselves cannot (SR6).
    """
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "PNG"
    if data.startswith(b"\xff\xd8\xff"):
        return "JPEG"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "WEBP"
    return None


def validate_image(data: bytes) -> ImageInfo | Rejection:
    """Return ImageInfo for an acceptable image, or a Rejection saying why not.

    Why: images come from untrusted webpages, so oversized, fake, animated or corrupt
    files must be stopped before any model touches them (FR2, SR6, H7).
    """
    # 1. Size: check the byte count first, before spending any effort decoding.
    if len(data) > MAX_IMAGE_SIZE:
        return Rejection("image_too_large", "Images must be 10.0 MB or smaller.")
    # 2. Format: only real PNG, JPEG or WebP bytes get through (blocks GIF, SVG, scripts).
    fmt = _sniff(data)
    if fmt is None:
        return Rejection("unsupported_format", "Only PNG, JPEG and WebP images are supported.")
    try:
        with warnings.catch_warnings():
            # Treat Pillow's "decompression bomb" warning as an error (tiny file, huge image).
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            # Only allow the sniffed format, so Pillow can't be tricked into another decoder.
            with Image.open(io.BytesIO(data), formats=[fmt]) as img:
                # 3. Dimensions: read from the header; pixels are not decoded yet.
                w, h = img.size
                if min(w, h) < MIN_IMAGE_DIM:
                    return Rejection(
                        "image_too_small", f"Images must be at least {MIN_IMAGE_DIM}px."
                    )
                if max(w, h) > MAX_IMAGE_DIM:
                    return Rejection("image_too_big", f"Images must be at most {MAX_IMAGE_DIM}px.")
                # 4. Static only: animated WebP/PNG frames are out of scope.
                if getattr(img, "n_frames", 1) > 1:
                    return Rejection("animated_image", "Animated images are not supported.")
                # 5. Full decode: catches files whose header is fine but whose data is broken.
                img.load()
                return ImageInfo(fmt, w, h, len(img.getexif()))
    except Exception:  # any decoder fault on untrusted input is a rejection, never a crash
        return Rejection("corrupt_image", "The image could not be read.")

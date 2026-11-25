"""Shared test helpers. pytest loads this file automatically for every test."""

import io

from PIL import Image

# A realistic 243-character news paragraph, long enough to pass the text length check.
SAMPLE_TEXT = (
    "The council met on Tuesday to review the proposed changes to the downtown bus routes. "
    "Several residents spoke in favour of extending evening service, while two business "
    "owners raised concerns about parking. A final vote is expected next month."
)


def make_image(fmt="PNG", size=(128, 96)) -> bytes:
    """Create a plain single-colour image in memory and return its file bytes.

    Why: tests get exact sizes and formats without committing image files to the repo.
    """
    buf = io.BytesIO()
    Image.new("RGB", size, (120, 80, 200)).save(buf, format=fmt)
    return buf.getvalue()

import io
from typing import Tuple

import requests
from PIL import Image

Thumb = Tuple[bytes, int, int]


def make_thumb_data(url: str, h=320, w=320, fmt="JPEG", timeout=5) -> Thumb:
    """ returns thumb data as bytes, width and height of thumb """
    img = Image.open(
        requests.get(
            url,
            stream=True,
            timeout=timeout,
        ).raw
    )

    img.thumbnail((w, h))
    width, height = img.size

    with io.BytesIO() as output:
        img.save(output, format=fmt)
        data = output.getvalue()

    return data, width, height

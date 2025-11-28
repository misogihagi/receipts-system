import pytest
import os
from src.services.image_conversion import ImageConversionService
from PIL import Image
import numpy as np

def create_minimal_tiff(filename="empty_image.tif", width=1, height=1):
    """
    Creates a minimal, all-black TIFF file using Pillow.

    Args:
        filename (str): The name of the file to save.
        width (int): The width of the minimal image in pixels.
        height (int): The height of the minimal image in pixels.
    """
    data = np.zeros((height, width), dtype=np.uint8)
    img = Image.fromarray(data, mode='L')
    img.save(filename, format='TIFF')


def test_convert_tiff_to_png():
    # Create a dummy TIFF file
    create_minimal_tiff("test.tiff", width=10, height=10)

    service = ImageConversionService()
    png_path = service.convert_tiff_to_png("test.tiff")
    assert png_path == "test.png"

    # Delete the dummy TIFF file
    os.remove("test.tiff")
    # Delete the created PNG file, if it exists
    if os.path.exists("test.png"):
        os.remove("test.png")

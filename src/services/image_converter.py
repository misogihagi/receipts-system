from PIL import Image, UnidentifiedImageError
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def convert_tiff_to_png(tiff_filepath: str, png_filepath: str) -> bool:
    """
    Converts a TIFF image to PNG format using the Pillow library.

    Args:
        tiff_filepath: The path to the TIFF image file.
        png_filepath: The path to save the converted PNG image file.

    Returns:
        True if the conversion was successful, False otherwise.
    """
    try:
        image = Image.open(tiff_filepath)
        image.save(png_filepath, "PNG")
        logging.info(f"Successfully converted {tiff_filepath} to {png_filepath}")
        return True
    except FileNotFoundError:
        logging.error(f"File not found: {tiff_filepath}")
        return False
    except UnidentifiedImageError:
        logging.error(f"Invalid file format or corrupted image data: {tiff_filepath}")
        return False
    except Exception as e:
        logging.error(f"Error converting {tiff_filepath} to PNG: {e}")
        return False
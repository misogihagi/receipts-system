import unittest
import os
import logging
from src.services.image_converter import convert_tiff_to_png
from io import StringIO


class TestImageConverter(unittest.TestCase):
    def test_convert_tiff_to_png_success(self):
        # Create a dummy TIFF file for testing
        from PIL import Image

        # Create a dummy TIFF file for testing
        image = Image.new("RGB", (100, 100), color="white")
        image.save("test.tiff", "TIFF")

        # Convert the TIFF file to PNG
        result = convert_tiff_to_png("test.tiff", "test.png")

        # Assert that the conversion was successful
        self.assertTrue(result)

        # Assert that the PNG file was created
        self.assertTrue(os.path.exists("test.png"))

        os.remove("test.tiff")
        os.remove("test.png")

    def test_convert_tiff_to_png_failure_file_not_found(self):
        # Attempt to convert a non-existent TIFF file
        result = convert_tiff_to_png("non_existent.tiff", "test.png")

        # Assert that the conversion failed
        self.assertFalse(result)

    def test_convert_tiff_to_png_failure_invalid_file_format(self):
        # Create an invalid TIFF file for testing
        with open("test.tiff", "w") as f:
            f.write("Invalid TIFF data")

        # Capture the log output
        with self.assertLogs(level="ERROR") as cm:
            # Attempt to convert the invalid TIFF file to PNG
            result = convert_tiff_to_png("test.tiff", "test.png")

            # Assert that the conversion failed
            self.assertFalse(result)

            # Assert that the correct logging message was written
            self.assertEqual(
                cm.output,
                ["ERROR:root:Invalid file format or corrupted image data: test.tiff"],
            )

        # Clean up the test file
        os.remove("test.tiff")


if __name__ == "__main__":
    unittest.main()

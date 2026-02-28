import unittest
import os
import logging
from src.services.webp_storage import store_webp_file
from io import StringIO
from datetime import datetime


class TestWebpStorage(unittest.TestCase):
    def setUp(self):
        self.logger = logging.getLogger("src.services.webp_storage")
        self.log_capture = StringIO()
        self.handler = logging.StreamHandler(self.log_capture)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)
        self.storage_directory = "test_storage"
        os.makedirs(self.storage_directory, exist_ok=True)

    def tearDown(self):
        # Clean up the created files and directories
        if os.path.exists(self.storage_directory):
            for root, dirs, files in os.walk(self.storage_directory, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(self.storage_directory)

    def test_store_webp_file_success(self):
        # Create a dummy WebP file for testing
        with open("test.webp", "w") as f:
            f.write("Dummy WebP data")

        # Store the WebP file
        new_filepath = store_webp_file("test.webp", self.storage_directory)

        # Assert that the storage was successful
        self.assertIsNotNone(new_filepath)

        # Assert that the file exists in the new location
        self.assertTrue(os.path.exists(new_filepath))

        # Assert that the file was moved
        self.assertFalse(os.path.exists("test.webp"))

    def test_store_webp_file_failure_file_not_found(self):
        # Attempt to store a non-existent WebP file
        result = store_webp_file("non_existent.webp", self.storage_directory)

        # Assert that the storage failed
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()

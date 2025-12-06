import unittest
import os
from unittest.mock import patch
import requests
from src.services.ocr_processor import OCRProcessor

class TestOCRProcessor(unittest.TestCase):

    @patch('requests.post')
    def test_process_document_success(self, mock_post):
        # Configure the mock to return a successful response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"document_id": 123}

        # Create a dummy image file for testing
        with open("test.png", "w") as f:
            f.write("Dummy PNG data")

        # Create an OCRProcessor instance
        ocr_processor = OCRProcessor("http://paperless.example.com", "test_api_token", ocr_language="jpn+eng")

        # Process the document
        result = ocr_processor.process_document("test.png")

        # Assert that the request was successful
        self.assertEqual(result, {"document_id": 123})

        # Clean up the created files
        os.remove("test.png")

    @patch('requests.post')
    def test_process_document_failure_file_not_found(self, mock_post):
        # Create an OCRProcessor instance
        ocr_processor = OCRProcessor("http://paperless.example.com", "test_api_token", ocr_language="jpn+eng")

        # Process the document
        result = ocr_processor.process_document("non_existent.png")

        # Assert that the request failed
        self.assertIsNone(result)

    @patch('requests.post')
    def test_process_document_failure_ocr_error(self, mock_post):
        # Configure the mock to return a successful response with an error message
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"error": "OCR failed to read text"}

        # Create a dummy image file for testing
        with open("test.png", "w") as f:
            f.write("Dummy PNG data")

        # Create an OCRProcessor instance
        ocr_processor = OCRProcessor("http://paperless.example.com", "test_api_token", ocr_language="jpn+eng")

        # Process the document
        result = ocr_processor.process_document("test.png")

        # Assert that the request failed
        self.assertIsNone(result)



if __name__ == '__main__':
    unittest.main()
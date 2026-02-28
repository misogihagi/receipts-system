import requests
import os
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class OCRProcessor:
    def __init__(self, paperless_url, api_token, ocr_language="eng"):
        self.paperless_url = paperless_url
        self.api_token = api_token
        self.ocr_language = ocr_language
        self.headers = {"Authorization": f"Token {self.api_token}"}

    def process_document(self, image_path):
        """Processes a document using the Paperless-ngx API."""
        try:
            with open(image_path, "rb") as image_file:
                files = {"document": image_file}
                data = {"title": os.path.basename(image_path)}
                data["language"] = self.ocr_language
                response = requests.post(
                    f"{self.paperless_url}/api/documents/post/",
                    headers=self.headers,
                    files=files,
                    data=data,
                )
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                response_json = response.json()
                if "error" in response_json:
                    logging.error(
                        f"Error processing {image_path}: {response_json['error']}"
                    )
                    return None
                logging.info(f"Successfully uploaded {image_path} to Paperless-ngx")
                return response_json
        except FileNotFoundError:
            logging.error(f"File not found: {image_path}")
            return None
        except requests.exceptions.RequestException as e:
            logging.error(f"Error uploading {image_path} to Paperless-ngx: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    paperless_url = os.environ.get("PAPERLESS_URL")
    api_token = os.environ.get("PAPERLESS_API_TOKEN")
    image_path = "test.png"
    ocr_language = "jpn+eng"

    if not paperless_url or not api_token:
        print(
            "Please set the PAPERLESS_URL and PAPERLESS_API_TOKEN environment variables."
        )
    else:
        ocr_processor = OCRProcessor(paperless_url, api_token, ocr_language)
        result = ocr_processor.process_document(image_path)
        if result:
            print(f"Successfully processed {image_path}")
            print(result)
        else:
            print(f"Failed to process {image_path}")

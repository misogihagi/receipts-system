import requests
import os

PAPERLESS_URL = "http://localhost:8765"
API_TOKEN = "c448f34127ee399c04d603d91978f9095fb18823"
FILE_PATH = "doc.png"

# --- Document Metadata ---
# This is the data that Paperless-ngx will use to classify the document
# For a full list of fields, refer to the Paperless-ngx API documentation
DOCUMENT_TITLE = "2024 Receipt for New Widget"
DOCUMENT_CORRESPONDENT_ID = (
    1  # Optional: Replace with the ID of the correspondent (e.g., vendor)
)
DOCUMENT_DOCUMENT_TYPE_ID = (
    2  # Optional: Replace with the ID of the document type (e.g., Receipt)
)
DOCUMENT_TAG_IDS = [5, 12]  # Optional: Replace with a list of Tag IDs to apply

# The actual endpoint for document upload
UPLOAD_ENDPOINT = "/api/documents/post_document/"


def upload_document(file_path: str, url: str, token: str):
    """
    Uploads a file and its associated metadata to Paperless-ngx.

    Args:
        file_path (str): The local path to the file to upload.
        url (str): The base URL of the Paperless-ngx instance.
        token (str): The API token for authentication.
    """
    full_url = url.rstrip("/") + UPLOAD_ENDPOINT

    # 1. Prepare Headers for Authentication
    headers = {
        "Authorization": f"Token {token}",
    }

    # 2. Prepare Metadata (Fields)
    # The API expects metadata fields to be submitted as 'data' parts, not 'files'.
    metadata_fields = {
        "title": DOCUMENT_TITLE,
        # "document_type": DOCUMENT_DOCUMENT_TYPE_ID,
        # "correspondent": DOCUMENT_CORRESPONDENT_ID,
        # "tags": DOCUMENT_TAG_IDS, # Note: Lists are handled correctly by the requests library for multipart/form-data
        # You can add more metadata fields here, e.g., 'archive_serial_number'
    }

    # 3. Prepare the File
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at: {file_path}")

        # Open the file in binary mode for upload
        with open(file_path, "rb") as f:
            # The 'files' dictionary is used to handle file uploads in multipart/form-data
            # 'document': This is the name of the file field expected by the Paperless-ngx API.
            files = {"document": (os.path.basename(file_path), f, "image/jpeg")}

            print(
                f"Attempting to upload '{DOCUMENT_TITLE}' from {file_path} to {full_url}"
            )

            # 4. Make the POST request
            # requests will automatically encode the 'metadata_fields' into the multipart body
            # along with the 'files'.
            response = requests.post(
                full_url,
                headers=headers,
                data=metadata_fields,
                files=files,
                timeout=30,  # Set a timeout for the request
            )

        # 5. Handle the Response
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        # Success handling
        if response.status_code == 200 or response.status_code == 201:
            print("\n✅ Document Upload Successful!")
            # The response body contains the new document's details (ID, etc.)
            new_document_data = response.json()
            print(new_document_data)
            print(f"   New Document ID: {new_document_data.get('id')}")
            print(f"   Document Title: {new_document_data.get('title')}")
            print(f"   Status Code: {response.status_code}")
        else:
            # Should be caught by raise_for_status, but kept for clarity
            print(f"\n❌ Upload Failed with status code: {response.status_code}")
            print(f"   Response Body: {response.text}")

    except FileNotFoundError as e:
        print(f"Fatal Error: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error during upload: {e}")
        print(f"   Response Text: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred during the request: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    # Ensure you replace the placeholder values at the top of the script
    # For this script to run successfully, you need a valid Paperless-ngx instance,
    # a correct API token, and a local JPEG file at the specified path.
    upload_document(FILE_PATH, PAPERLESS_URL, API_TOKEN)

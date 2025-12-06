import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def store_webp_file(webp_filepath: str, storage_directory: str) -> str:
    """
    Stores a WebP file in a structured directory based on the date.

    Args:
        webp_filepath: The path to the WebP file.
        storage_directory: The root directory to store the WebP files.

    Returns:
        The path to the stored WebP file, or None if the storage failed.
    """
    try:
        # Get the current date
        now = datetime.now()
        date_string = now.strftime("%Y/%m/%d")

        # Create the directory path
        directory_path = os.path.join(storage_directory, date_string)

        # Create the directory if it doesn't exist
        os.makedirs(directory_path, exist_ok=True)

        # Get the filename
        filename = os.path.basename(webp_filepath)

        # Create the new filepath
        new_filepath = os.path.join(directory_path, filename)

        # Move the file to the new location
        os.rename(webp_filepath, new_filepath)

        logging.info(f"Successfully stored {webp_filepath} to {new_filepath}")
        return new_filepath
    except FileNotFoundError:
        logging.error(f"File not found: {webp_filepath}")
        return None
    except Exception as e:
        logging.error(f"Error storing {webp_filepath}: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    webp_file = "test.webp"
    storage_directory = "storage"
    try:
        os.makedirs(storage_directory, exist_ok=True)
        with open(webp_file, "w") as f:
            f.write("Dummy WebP data")

        new_filepath = store_webp_file(webp_file, storage_directory)
        if new_filepath:
            print(f"Successfully stored {webp_file} to {new_filepath}")
        else:
            print(f"Failed to store {webp_file}")
    finally:
        if os.path.exists(storage_directory):
            for filename in os.listdir(storage_directory):
                file_path = os.path.join(storage_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(storage_directory)
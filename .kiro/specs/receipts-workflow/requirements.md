# Requirements Document

## Project Description (Input)

workflow: 1. scan receipts as tif 2. convert to png file 3. ocr png file 4. convert png to webp 5. store webp files 6. post data to paperless-ngx

## Requirements

### 1.
- images/
ファイルのスキャン: images/ ディレクトリ内の .zip ファイルをリストアップする。

解凍処理: 一時フォルダ（temp/ など）を作成し、ファイルを解凍する。

データの読み込み: 解凍されたファイル（画像やメタデータ）を読み込み、APIが受け取れる形式（Base64変換やバイナリ形式）に整形する。
画像はハッシュ値を出し状態は例の通り、ハッシュマップとして保持する。
画像はtiff形式なので容量削減のためwebpに変換する。

APIを使わない格納：APIを使うと余計なOCRの処理やカスタマイズができないので直接処理する
データベースの直接編集
解析済みのファイルの配置

後処理: 送信が成功したZIPファイルを「処理済みフォルダ」に移動、または削除する。

# status.yaml のイメージ
processed_files:
  aaabbbccc:
    status: "success"
    processed_at: "2024-05-20 10:00:00"
  bbbcccddd:
    status: "failed"
    message: "API Timeout"
    processed_at: "2024-05-20 10:05:00"

### 1. Image Conversion (TIFF to PNG)
- The system must convert TIFF images to PNG format using the Pillow library.
- Pillow version: [Specify version]
- Error handling: The system must handle potential exceptions during the conversion process, such as invalid file format or corrupted image data.
- Logging: Log successful and failed conversions.

### 2. OCR Processing (PNG)
- The system must use Paperless-ngx's built-in OCR capabilities to extract text from the PNG image.
- The system must be configured to use both Japanese and English languages for OCR.
- The system should handle potential OCR errors, such as unreadable text or recognition failures.
- Logging: Log successful and failed OCR operations.

### 3. Image Conversion (PNG to WebP)
- The system must convert the PNG image to WebP format using the Pillow library.
- Pillow version: [Specify version]
- The system should use appropriate compression settings and quality levels for WebP conversion.
- Error handling: The system must handle potential exceptions during the conversion process.
- Logging: Log successful and failed conversions.

### 4. WebP Storage
- The system must store the WebP files in a structured directory.
- The naming convention for the WebP files should be unique (e.g., using a unique ID).
- The system must ensure that the WebP files are stored securely and with appropriate permissions.
- Logging: Log successful and failed file storage operations.

### 5. Paperless-ngx API Integration
- The system must post the extracted data to the Paperless-ngx REST API.
- API endpoint: [Specify endpoint]
- Data format: [Specify data format, e.g., JSON schema]
- The system must use an API key for authentication.
- The API key must be stored securely (e.g., as an environment variable).
- Error handling: The system must handle API responses and potential errors, such as invalid API key or server errors.
- Logging: Log successful and failed API requests.

### 6. Security Considerations
- The Paperless-ngx API key must be stored securely and should not be hardcoded in the code.
- Implement appropriate input validation and sanitization to prevent security vulnerabilities.

### 7. Logging
- The system must log key events during the workflow for debugging and auditing.
- Log messages should include timestamps, event descriptions, and relevant data.

### 8. Error Handling
- The system must handle errors gracefully and provide informative error messages.
- Implement appropriate error recovery mechanisms.

### 9. Technology Selection
- Python
- Pillow
- Paperless-ngx

### 10. File Structure
- Follow the project structure defined in `.kiro/steering/structure.md`.

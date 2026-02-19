import os
import traceback
import zipfile
import shutil
import hashlib
import base64
import requests
import yaml
from datetime import datetime
from pathlib import Path

# --- 設定 ---
IMAGE_DIR = Path("images")
TEMP_DIR = Path("temp")
STATUS_FILE = Path("status.yaml")


def preprocess():
    for d in [IMAGE_DIR, TEMP_DIR]:
        d.mkdir(exist_ok=True)


def get_file_hash(file_path):
    """ファイルのSHA-256ハッシュ値を計算"""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def load_status():
    """status.yamlを読み込む"""
    if STATUS_FILE.exists():
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {"processed_files": {}}
    return {"processed_files": {}}


def save_status(status_data):
    """status.yamlに書き込む"""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        yaml.dump(status_data, f, allow_unicode=True, sort_keys=False)


def process_zip():
    status_data = load_status()
    zip_files = list(IMAGE_DIR.glob("*.zip"))

    if not zip_files:
        print("処理対象のZIPファイルが見つかりません。")
        return

    for zip_path in zip_files:
        print(f"処理中: {zip_path.name}")

        # 1. 解凍
        extract_path = TEMP_DIR / zip_path.stem
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)

        try:
            # 2. データの読み込みと整形
            image_payloads = []
            for img_file in extract_path.rglob("*"):
                if img_file.suffix.lower() in [".tif", ".TIF"]:
                    print(img_file)
                    img_hash = get_file_hash(img_file)

                    with open(img_file, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode("utf-8")

                    image_payloads.append(
                        {
                            "hash": img_hash,
                            "filename": img_file.name,
                            "data": encoded_string,
                        }
                    )

            # 3. API送信

            status_code = 200
            if status_code == 200:
                # ファイル削除
                # os.remove(TEMP_DIR / zip_path.name)
                pass
            else:
                raise Exception(f"API Error: {status_code}")

        except Exception as e:
            # 失敗時の処理
            print(f"失敗: {zip_path.name} - {str(e)}")
            print(traceback.format_exc())
            status_data["processed_files"][zip_path.name] = {
                "status": "failed",
                "message": str(e),
                "filename": img_file.name,
                "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

        finally:
            # 一時フォルダの削除
            if extract_path.exists():
                shutil.rmtree(extract_path)

    # 4. 状態の保存
    save_status(status_data)


if __name__ == "__main__":
    process_zip()

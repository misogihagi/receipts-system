import os
import traceback
import zipfile
import shutil
import hashlib
import base64
import requests
import yaml
import fitz
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from paddleocr import PaddleOCR

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

def ocr(img_file):
    ocr = PaddleOCR(lang="japan")
    return ocr.predict(img_file)

def create_pdf(data, image_path, pdf_path):
    polygons = data["rec_boxes"]
    texts = data["rec_texts"]

    if not os.path.exists(image_path):
        print(f"Error: 画像ファイルが見つかりません: {image_path}")
        return

    doc = fitz.open()
    img_doc = fitz.open(image_path)

    def px_to_pt(px):
        dpi = img_doc[0].get_image_info()[0].get("xres", 72)
        return px * (72 / dpi)

    # 画像のサイズに合わせてページを作成
    img_rect = img_doc[0].rect
    page = doc.new_page(width=img_rect.width, height=img_rect.height)

    page.insert_image(img_rect, filename=image_path)

    # 透明テキストの埋め込み

    for text, poly in zip(texts, polygons):
        if not text.strip():
            continue

        # poly[0]が左上、poly[2]が右下の想定
        x0, y0 = (poly[0], poly[1])
        x2, y2 = (poly[2], poly[3])

        # テキストの高さからフォントサイズを決定
        line_height = abs(y2 - y0)
        font_size = line_height * 0.75  # 調整係数

        # insert_textのポイントは(x, y)で、yはベースライン（文字の下端）
        # そのため、y2（矩形の下端）に近い位置を指定する
        page.insert_text(
            (px_to_pt(x0), px_to_pt(y2 - (line_height * 0.1))),
            text,
            fontsize=px_to_pt(font_size),
            render_mode=3,  # 0:塗りつぶし, 3:透明
        )

    doc.save(pdf_path)
    doc.close()
    img_doc.close()

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

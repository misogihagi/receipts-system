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
import torch
from transformers import pipeline

from datetime import date, datetime
from pathlib import Path
from paddleocr import PaddleOCR
from PIL import Image
from sqlalchemy import Column, Date, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base

IMAGE_DIR = Path("data/images")
TEMP_DIR = Path("data/temp")
OUTPUT_DIR = Path("data/docker/media/documents")
ARCHIVE_DIR = OUTPUT_DIR / Path("archive")
ORIGINAL_DIR = OUTPUT_DIR / Path("originals")
THUMBNAIL_DIR = OUTPUT_DIR / Path("thumbnails")
STATUS_FILE = Path("data/status.yaml")

DATABASE_URI = "sqlite:///data/docker/data/db.sqlite3"
OWNER_ID = 3

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents_document"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    modified = Column(DateTime, nullable=False)
    correspondent_id = Column(Integer, nullable=True)
    checksum = Column(String(32), nullable=False, unique=True)
    added = Column(DateTime, nullable=False)
    storage_type = Column(String(11), nullable=False)
    filename = Column(String(1024), unique=True)
    archive_serial_number = Column(Integer, unique=True)
    document_type_id = Column(Integer, nullable=True)
    mime_type = Column(String(256), nullable=False)
    archive_checksum = Column(String(32))
    archive_filename = Column(String(1024), unique=True)
    storage_path_id = Column(Integer, nullable=True)
    original_filename = Column(String(1024))
    owner_id = Column(Integer, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    restored_at = Column(DateTime, nullable=True)
    transaction_id = Column(String(32))
    page_count = Column(Integer)
    created = Column(Date, nullable=False)


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


def generate_title(content):
    pipe = pipeline(
        "text-generation",
        model="google/gemma-2-2b-jpn-it",
        model_kwargs={"torch_dtype": torch.bfloat16},
        device="cpu",  # replace with "mps" to run on a Mac device
    )

    messages = [
        {
            "role": "user",
            "content": "以下はレシートのOCR結果です。これを見て「どこで」「何を」買ったのかひと目でわかるタイトルをプレーンテキストで30文字以内で出力してください。\n"
            + content,
        },
    ]

    outputs = pipe(messages, return_full_text=False)
    assistant_response = outputs[0]["generated_text"].strip()
    return assistant_response


def predict_date(content):

    for _ in range(10):
        pipe = pipeline(
            "text-generation",
            model="google/gemma-2-2b-jpn-it",
            model_kwargs={"torch_dtype": torch.bfloat16},
            device="cpu",  # replace with "mps" to run on a Mac device
        )

        messages = [
            {
                "role": "user",
                "content": "以下はレシートのOCR結果です。これを見ていつのレシートかを「YYYY年MM月DD日」形式で出力してください。\n"
                + content,
            },
        ]

        outputs = pipe(messages, return_full_text=False)
        assistant_response = outputs[0]["generated_text"].strip()
        try:
            date = datetime.strptime(assistant_response, "%Y年%m月%d日").date()
            return date
        except:
            pass


def calculate_checksum(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def insert_database(
    title,
    content,
    checksum,
    filename,
    archive_checksum,
    archive_filename,
    original_filename,
    created,
):
    engine = create_engine(DATABASE_URI)
    with Session(engine) as session:
        new_doc = Document(
            title=title,
            content=content,
            modified=datetime.now(),
            checksum=checksum,
            added=datetime.now(),
            storage_type="unencrypted",
            filename=filename,
            mime_type="image/webp",
            archive_checksum=archive_checksum,
            archive_filename=archive_filename,
            original_filename=original_filename,
            owner_id=OWNER_ID,
            created=created,
        )
        session.add(new_doc)
        session.commit()
        return new_doc.id


def process_image(img_file):
    with Image.open(img_file) as original_img:
        # 現在のサイズを取得
        width, height = original_img.size

        # サイズを半分に計算（整数にする必要があるため // 2）
        new_size = (width // 2, height // 2)

        # PaddleOCRは4000以上はリサイズされるので予めしておく
        # Resized image size (5104x7016) exceeds max_side_limit of 4000. Resizing to fit within limit.
        # リサイズ（Image.LANCZOSは高品質な補完アルゴリズムです）
        img = original_img.resize(new_size, Image.LANCZOS)

        hash = get_file_hash(img_file)

        # WebP形式で保存
        # qualityは0-100で指定可能（デフォルトは80程度）
        webp_file = Path(str(ORIGINAL_DIR) + "/" + hash + ".webp")
        img.save(str(webp_file), "WEBP", quality=80)

        # PaddleOCRはTIFFを読めないのでPNG形式に変換
        png_file = Path(str(TEMP_DIR) + "/" + hash + ".png")

        img.save(str(png_file), format="PNG")

        # RGBAの場合はRGBに変換（透過を白背景にする）
        jpeg_file = Path(str(TEMP_DIR) + "/" + hash + ".jpeg")
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img.save(str(jpeg_file), "JPEG", quality=95)

    result = ocr(str(png_file))

    res = result[0]

    pdf_file = Path(str(ARCHIVE_DIR) + "/" + hash + ".pdf")
    create_pdf(res, str(jpeg_file), str(pdf_file))

    content = "\n".join(res["rec_texts"])
    title = generate_title(content)
    created = predict_date(content) or date.today()
    checksum = calculate_checksum(webp_file)
    archive_checksum = calculate_checksum(pdf_file)
    original_filename = img_file.name
    doc_id = insert_database(
        title,
        content,
        checksum,
        webp_file.name,
        archive_checksum,
        pdf_file.name,
        original_filename,
        created,
    )
    with Image.open(img_file) as original_img:
        # サムネイルの生成
        thumbnail_file = Path(str(THUMBNAIL_DIR) + "/" + str(doc_id).zfill(7) + ".webp")
        # 横が500ピクセルになるようリサイズ
        width_size = 500
        height_size = int((float(img.size[1]) * float(width_size / img.size[0])))
        resized_img = img.resize((width_size, height_size), Image.LANCZOS)
        resized_img.save(str(thumbnail_file), "WEBP", quality=80)

    os.remove(png_file)
    os.remove(jpeg_file)


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
                    img_hash = get_file_hash(img_file)

                    with open(img_file, "rb") as f:
                        encoded_string = base64.b64encode(f.read()).decode("utf-8")

                    process_image(img_file)

                    image_payloads.append(
                        {
                            "hash": img_hash,
                            "filename": date.fromisoformat("2026-02-13"),
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

from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang="japan"  # 認識する言語を日本語に設定します
)
result = ocr.predict("./doc.png")
for res in result:
    res.print()
    res.save_to_img("output")
    res.save_to_json("output")

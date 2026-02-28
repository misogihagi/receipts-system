from PIL import Image


class ImageConversionService:
    def convert_tiff_to_png(self, tiff_path):
        try:
            image = Image.open(tiff_path)
            png_path = tiff_path.replace(".tiff", ".png")
            image.save(png_path, "PNG")
            return png_path
        except FileNotFoundError:
            print(f"File not found: {tiff_path}")
            return None

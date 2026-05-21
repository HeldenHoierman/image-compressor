"""
Image compressor.

Modes:
  python compress_images.py file1 file2 ...    drag-drop via .bat (console, pause at end)
  pythonw compress_images.py --silent file1    registry right-click (no console, no output)
"""

import sys
import os
from PIL import Image

# ── Settings ──────────────────────────────────────────────────────────────────

JPEG_QUALITY    = 75
JPEG_SUBSAMPLING = 0   # 0 = 4:4:4 (best chroma quality)
PNG_COMPRESS    = 9    # lossless, max compression
WEBP_QUALITY    = 80

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}

# ─────────────────────────────────────────────────────────────────────────────

def format_bytes(n):
    if n < 1024:
        return f"{n} B"
    elif n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    else:
        return f"{n / 1024 ** 2:.2f} MB"


def compress(path, silent=False):
    def log(msg):
        if not silent:
            print(msg)

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED:
        log(f"  SKIP  {os.path.basename(path)}  (unsupported type)")
        return 0

    original_size = os.path.getsize(path)

    try:
        img = Image.open(path)
        fmt = img.format
    except Exception:
        return 0

    tmp_path = path + ".compressing.tmp"

    try:
        if ext in ('.jpg', '.jpeg'):
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            img.save(tmp_path, format='JPEG', quality=JPEG_QUALITY,
                     optimize=True, progressive=True, subsampling=JPEG_SUBSAMPLING)

        elif ext == '.png':
            if img.mode not in ('RGBA', 'RGB', 'L'):
                img = img.convert('RGBA' if 'A' in img.getbands() else 'RGB')
            img.save(tmp_path, format='PNG', optimize=True, compress_level=PNG_COMPRESS)

        elif ext == '.webp':
            img.save(tmp_path, format='WEBP', quality=WEBP_QUALITY, method=6)

        elif ext in ('.bmp', '.tiff', '.tif'):
            if img.mode in ('RGBA', 'P', 'LA'):
                img = img.convert('RGB')
            new_path = os.path.splitext(path)[0] + '.jpg'
            img.save(new_path, format='JPEG', quality=JPEG_QUALITY,
                     optimize=True, progressive=True)
            compressed_size = os.path.getsize(new_path)
            saved = original_size - compressed_size
            pct = (saved / original_size) * 100 if original_size else 0
            if saved > 0:
                os.remove(path)
                log(f"  OK    {os.path.basename(path)} -> .jpg  "
                    f"{format_bytes(original_size)} -> {format_bytes(compressed_size)}  "
                    f"(-{pct:.1f}%)")
            else:
                os.remove(new_path)
                log(f"  SKIP  {os.path.basename(path)}  (already optimal)")
            return max(saved, 0)

        else:
            img.save(tmp_path, format=fmt, optimize=True)

    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return 0
    finally:
        img.close()

    compressed_size = os.path.getsize(tmp_path)
    saved = original_size - compressed_size
    pct = (saved / original_size) * 100 if original_size else 0

    if saved > 0:
        try:
            os.replace(tmp_path, path)
        except Exception:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return 0
        log(f"  OK    {os.path.basename(path)}  "
            f"{format_bytes(original_size)} -> {format_bytes(compressed_size)}  "
            f"(-{pct:.1f}%)")
    else:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        log(f"  SKIP  {os.path.basename(path)}  (already optimal)")

    return max(saved, 0)


def main():
    args = sys.argv[1:]

    silent = '--silent' in args
    files = [a for a in args if a != '--silent']

    if not files:
        if not silent:
            print("No files provided.")
            print("Drag image files onto 'Compress Images.bat', or")
            print("right-click any image and choose 'Compress Image(s)'.")
            input("\nPress Enter to exit...")
        return

    if not silent:
        print(f"\nCompressing {len(files)} file(s)...\n")

    total_saved = 0
    for path in files:
        path = path.strip('"')
        if os.path.isfile(path):
            total_saved += compress(path, silent=silent)

    if not silent:
        print(f"\nDone.  Total saved: {format_bytes(total_saved)}")
        input("\nPress Enter to close...")


if __name__ == '__main__':
    main()

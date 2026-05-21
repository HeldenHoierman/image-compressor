"""
Image compressor.

Modes:
  python compress_images.py file1 file2 ...    drag-drop via .bat (console, pause at end)
  pythonw compress_images.py --silent file1    registry right-click (no console, no output)

In silent mode: runs invisibly. If any errors occur, shows a Windows
MessageBox listing them so nothing fails without explanation.
"""

import sys
import os
import traceback
import ctypes

# ── Settings ──────────────────────────────────────────────────────────────────

JPEG_QUALITY     = 75
JPEG_SUBSAMPLING = 0   # 0 = 4:4:4 (best chroma quality)
PNG_COMPRESS     = 9   # lossless, max compression
WEBP_QUALITY     = 80

SUPPORTED = {'.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff', '.tif'}

# ─────────────────────────────────────────────────────────────────────────────

def show_error(message):
    """Show a Windows error dialog. Works from pythonw.exe (no console required)."""
    ctypes.windll.user32.MessageBoxW(0, message, "Image Compressor — Error", 0x10)


def format_bytes(n):
    if n < 1024:
        return f"{n} B"
    elif n < 1024 ** 2:
        return f"{n / 1024:.1f} KB"
    else:
        return f"{n / 1024 ** 2:.2f} MB"


def compress(path, silent=False):
    """
    Compress a single image in place.
    Returns (bytes_saved, error_message_or_None).
    """
    def log(msg):
        if not silent:
            print(msg)

    ext = os.path.splitext(path)[1].lower()
    if ext not in SUPPORTED:
        log(f"  SKIP  {os.path.basename(path)}  (unsupported type)")
        return 0, None

    try:
        original_size = os.path.getsize(path)
    except OSError as e:
        return 0, f"{os.path.basename(path)}: cannot read file — {e}"

    try:
        img = Image.open(path)
        fmt = img.format
    except Exception as e:
        return 0, f"{os.path.basename(path)}: cannot open image — {e}"

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
            return max(saved, 0), None

        else:
            img.save(tmp_path, format=fmt, optimize=True)

    except Exception as e:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass
        return 0, f"{os.path.basename(path)}: compression failed — {e}"
    finally:
        img.close()

    compressed_size = os.path.getsize(tmp_path)
    saved = original_size - compressed_size
    pct = (saved / original_size) * 100 if original_size else 0

    if saved > 0:
        try:
            os.replace(tmp_path, path)
        except Exception as e:
            try:
                os.remove(tmp_path)
            except Exception:
                pass
            return 0, f"{os.path.basename(path)}: could not overwrite original — {e}"
        log(f"  OK    {os.path.basename(path)}  "
            f"{format_bytes(original_size)} -> {format_bytes(compressed_size)}  "
            f"(-{pct:.1f}%)")
    else:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        log(f"  SKIP  {os.path.basename(path)}  (already optimal)")

    return max(saved, 0), None


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
    errors = []

    for path in files:
        path = path.strip('"')
        if os.path.isfile(path):
            saved, err = compress(path, silent=silent)
            total_saved += saved
            if err:
                errors.append(err)
                if not silent:
                    print(f"  ERROR {err}")
        else:
            msg = f"{os.path.basename(path)}: file not found"
            errors.append(msg)
            if not silent:
                print(f"  MISS  {msg}")

    if silent and errors:
        show_error(
            f"{len(errors)} error(s) occurred:\n\n" +
            "\n".join(f"  {e}" for e in errors)
        )

    if not silent:
        print(f"\nDone.  Total saved: {format_bytes(total_saved)}")
        if errors:
            print(f"\n{len(errors)} error(s):")
            for e in errors:
                print(f"  {e}")
        input("\nPress Enter to close...")


# Top-level guard — catches import errors and total crashes in silent mode
try:
    from PIL import Image
except ImportError:
    if '--silent' in sys.argv:
        show_error(
            "Pillow is not installed.\n\n"
            "Run this in a terminal to fix it:\n\n"
            "    pip install Pillow"
        )
    else:
        print("ERROR: Pillow is not installed. Run: pip install Pillow")
        input("\nPress Enter to exit...")
    sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        if '--silent' in sys.argv:
            show_error(f"Unexpected error:\n\n{traceback.format_exc()}")
        else:
            raise

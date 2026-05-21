# Image Compressor

Compresses JPG, PNG, WebP, BMP, and TIFF files in place. Two ways to use it:

| Method | How |
|--------|-----|
| **Right-click menu** | Install once, then right-click any image → "Compress Image(s)" |
| **Drag and drop** | Drag image files onto `Compress Images.bat` |

---

## Setup

### Right-click menu (recommended)

```
Double-click install_menu.bat
```

No admin required. Writes to `HKCU` — current user only.
To remove: double-click `uninstall_menu.bat`.

### Drag and drop

Just drag image files onto `Compress Images.bat`. No installation needed.

---

## Behavior

- Originals are overwritten in place
- Files are silently skipped if compression would make them larger
- BMP and TIFF are converted to `.jpg` (originals deleted)
- Right-click mode is fully silent — no console, no popup
- Drag-drop mode shows a console window with per-file results and total saved

---

## Compression Settings

Adjust at the top of `compress_images.py`:

| Format | Setting | Default |
|--------|---------|---------|
| JPEG | `JPEG_QUALITY` | 75 (range: 1–95) |
| PNG | `PNG_COMPRESS` | 9 (lossless, max compression) |
| WebP | `WEBP_QUALITY` | 80 |

---

## Requirements

- Python 3.x on PATH
- Pillow: `pip install Pillow`

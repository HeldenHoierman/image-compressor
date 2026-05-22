"""
Image Compressor — Settings configurator.
Run directly or via Configure.bat to adjust compression quality settings.
"""

import json
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

DEFAULTS = {
    "jpeg_quality":     75,
    "jpeg_subsampling": 0,
    "png_compress":     9,
    "webp_quality":     80,
}

SUBSAMPLING_LABELS = {0: "4:4:4 (best)", 1: "4:2:2", 2: "4:2:0 (smallest)"}


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
            # Fill in any missing keys from defaults
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)
        f.write("\n")


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def divider():
    print("─" * 44)


def print_menu(cfg, dirty):
    clear()
    title = "Image Compressor — Settings"
    if dirty:
        title += "  (unsaved)"
    print(f"\n  {title}")
    divider()
    print(f"  1.  JPEG Quality      {cfg['jpeg_quality']:>3}        (1–95)")
    print(f"  2.  WebP Quality      {cfg['webp_quality']:>3}        (1–95)")
    print(f"  3.  PNG Compression   {cfg['png_compress']:>3}        (0–9, lossless)")
    sub_label = SUBSAMPLING_LABELS.get(cfg["jpeg_subsampling"], str(cfg["jpeg_subsampling"]))
    print(f"  4.  JPEG Subsampling  {sub_label}")
    divider()
    print("  S.  Save and exit")
    print("  Q.  Quit without saving\n")


def prompt_int(label, lo, hi, current):
    while True:
        raw = input(f"  {label} [{current}] ({lo}–{hi}): ").strip()
        if raw == "":
            return current
        if raw.lstrip("-").isdigit():
            val = int(raw)
            if lo <= val <= hi:
                return val
        print(f"  Please enter a number between {lo} and {hi}, or press Enter to keep current.")


def prompt_subsampling(current):
    print()
    for k, v in SUBSAMPLING_LABELS.items():
        marker = " <" if k == current else ""
        print(f"    {k}  {v}{marker}")
    while True:
        raw = input(f"\n  Choose [0/1/2] (Enter to keep {current}): ").strip()
        if raw == "":
            return current
        if raw in ("0", "1", "2"):
            return int(raw)
        print("  Enter 0, 1, or 2.")


def main():
    cfg = load_config()
    dirty = False

    while True:
        print_menu(cfg, dirty)
        choice = input("  Select: ").strip().lower()

        if choice == "1":
            cfg["jpeg_quality"] = prompt_int("New JPEG Quality", 1, 95, cfg["jpeg_quality"])
            dirty = True
        elif choice == "2":
            cfg["webp_quality"] = prompt_int("New WebP Quality", 1, 95, cfg["webp_quality"])
            dirty = True
        elif choice == "3":
            cfg["png_compress"] = prompt_int("New PNG Compression", 0, 9, cfg["png_compress"])
            dirty = True
        elif choice == "4":
            cfg["jpeg_subsampling"] = prompt_subsampling(cfg["jpeg_subsampling"])
            dirty = True
        elif choice == "s":
            save_config(cfg)
            clear()
            print("\n  Settings saved.\n")
            break
        elif choice == "q":
            clear()
            if dirty:
                print("\n  Changes discarded.\n")
            break
        else:
            pass  # invalid input — just redraw


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print("\n  Cancelled.\n")
        sys.exit(0)

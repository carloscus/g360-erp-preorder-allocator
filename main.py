#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

LOG = BASE_DIR / "error.log"

try:
    import flet as ft
    from src.app import main
except Exception as e:
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(f"ImportError: {e}\n")
        traceback.print_exc(file=f)
    print(f"Error de importacion: {e}", flush=True)
    sys.exit(1)

if __name__ == "__main__":
    try:
        ft.run(main)
    except SystemExit:
        raise
    except Exception as e:
        with open(LOG, "w", encoding="utf-8") as f:
            f.write(f"RuntimeError: {e}\n")
            traceback.print_exc(file=f)
        print(f"Error: {e}", flush=True)
        sys.exit(1)

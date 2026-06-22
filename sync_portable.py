import os
import shutil

FILES_TO_SYNC = [
    "main.py",
    "run.bat",
    "pyproject.toml",
    "requirements.txt",
    ".python-version",
    "uv.lock",
]

DIRS_TO_SYNC = [
    "src",
    "assets",
]


def sync_dir(src, dst):
    if not os.path.exists(src):
        return
    os.makedirs(dst, exist_ok=True)

    dst_items = set(os.listdir(dst))
    src_items = set(os.listdir(src))

    for item in dst_items - src_items:
        dst_item = os.path.join(dst, item)
        if os.path.isdir(dst_item):
            shutil.rmtree(dst_item)
            print(f"  Eliminado: {item}/")
        else:
            os.remove(dst_item)
            print(f"  Eliminado: {item}")

    for item in src_items:
        src_item = os.path.join(src, item)
        dst_item = os.path.join(dst, item)
        if os.path.isdir(src_item):
            sync_dir(src_item, dst_item)
        else:
            src_stat = os.stat(src_item)
            if not os.path.exists(dst_item) or os.stat(dst_item).st_mtime != src_stat.st_mtime or os.stat(dst_item).st_size != src_stat.st_size:
                shutil.copy2(src_item, dst_item)
                print(f"  Sincronizado: {item}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    portable_dir = os.path.join(base_dir, "g360-preorder-allocator-portable")

    os.makedirs(portable_dir, exist_ok=True)

    print("Sincronizando version portable...\n")

    for filename in FILES_TO_SYNC:
        src = os.path.join(base_dir, filename)
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(portable_dir, filename))
            print(f"  Copiado: {filename}")

    for dirname in DIRS_TO_SYNC:
        sync_dir(os.path.join(base_dir, dirname), os.path.join(portable_dir, dirname))

    print(f"\nSincronizacion finalizada con exito!")
    print(f"Portable listo en: {portable_dir}")


if __name__ == "__main__":
    main()

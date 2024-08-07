import os
import shutil

def copy_images(src, dest):
    if not os.path.exists(dest):
        os.makedirs(dest)

    for root, dirs, files in os.walk(src):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.svg')):
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest, file)
                shutil.copy(src_file, dest_file)
                print(f"Copied {src_file} to {dest_file}")

src_dir = r"E:\images\xiaomi画报"
dest_dir = r"E:\images\all_images"

copy_images(src_dir, dest_dir)

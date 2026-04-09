import os
import shutil
import urllib.request
import zipfile
import argparse
import tempfile
import sys

def download_file(url, dest_path):
    print(f"Downloading from {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print("Download complete.")
    except Exception as e:
        print(f"Failed to download from {url}: {e}")
        sys.exit(1)

def update_binaries(zip_path, binaries_dir):
    if not os.path.exists(binaries_dir):
        os.makedirs(binaries_dir)

    print(f"Clearing current binaries directory: {binaries_dir}...")
    for item in os.listdir(binaries_dir):
        item_path = os.path.join(binaries_dir, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except Exception as e:
            print(f"Warning: could not remove {item_path}: {e}")

    print(f"Extracting {zip_path} into {binaries_dir}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Check if there is a root folder inside the zip
            top_level = [name for name in zip_ref.namelist() if not name.startswith('/')]
            if top_level:
                # Basic extraction
                zip_ref.extractall(binaries_dir)
        print("Extraction complete. Binaries updated successfully.")
    except Exception as e:
        print(f"Failed to extract {zip_path}: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Update the binaries directory from a ZIP file (URL or local path).")
    parser.add_argument('source', help="URL or local path to the ZIP file containing the new binaries.")
    args = parser.parse_args()

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    binaries_dir = os.path.join(project_root, 'binaries')

    if args.source.startswith('http://') or args.source.startswith('https://'):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            tmp_zip_path = tmp_file.name

        try:
            download_file(args.source, tmp_zip_path)
            update_binaries(tmp_zip_path, binaries_dir)
        finally:
            if os.path.exists(tmp_zip_path):
                os.remove(tmp_zip_path)
    else:
        if not os.path.isfile(args.source):
            print(f"Error: Local file {args.source} does not exist.")
            sys.exit(1)
        update_binaries(args.source, binaries_dir)

if __name__ == '__main__':
    main()

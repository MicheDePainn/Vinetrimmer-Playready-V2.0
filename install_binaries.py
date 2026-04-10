import os
import sys
import io
import shutil
import zipfile
import urllib.request
import urllib.error

BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "binaries"))

SOURCES = {
    "aria2": "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip",
    "bento4": "https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-microsoft-win32.zip",
    "ccextractor": "https://github.com/CCExtractor/ccextractor/releases/download/v0.96.6/CCExtractor.0.96.6_win_portable.zip",
    "ffmpeg": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
    "mkvtoolnix": "https://mkvtoolnix.download/windows/releases/98.0/mkvtoolnix-64-bit-98.0.zip",
    "n_m3u8dl-re": "https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.5.1-beta/N_m3u8DL-RE_v0.5.1-beta_win-x64_20251029.zip",
    "packager": "https://github.com/shaka-project/shaka-packager/releases/download/v3.7.2/packager-win-x64.exe",
    "subtitleedit": "https://github.com/SubtitleEdit/subtitleedit/releases/download/4.0.15/SE4015.zip",
    "curl": "https://curl.se/windows/dl-8.19.0_6/curl-8.19.0_6-win64-mingw.zip"
}

def download_file(url, dest_path=None):
    print(f"Downloading {url}...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            content = response.read()
    except urllib.error.URLError as e:
        print(f"Error downloading {url}: {e}")
        return None
    
    if dest_path:
        with open(dest_path, "wb") as f:
            f.write(content)
        return dest_path
    else:
        return io.BytesIO(content)

def extract_flat(zip_bytes, target_dir):
    if zip_bytes is None:
        return
    with zipfile.ZipFile(zip_bytes) as z:
        for file_info in z.infolist():
            if file_info.is_dir():
                continue
            
            preserve_dirs = ['Dictionaries/', 'Tesseract302/', 'Languages/', 'Icons/', 'data/']
            filename = file_info.filename
            dest_rel_path = None
            
            for p_dir in preserve_dirs:
                if p_dir in filename:
                    dest_rel_path = filename[filename.find(p_dir):]
                    break
            
            if dest_rel_path:
                dest = os.path.join(target_dir, dest_rel_path)
            elif filename.lower().endswith(('.exe', '.dll')):
                dest = os.path.join(target_dir, os.path.basename(filename))
            else:
                continue

            # Special rename for CCExtractor
            if os.path.basename(dest).lower() == "ccextractorwinfull.exe":
                dest = os.path.join(target_dir, "ccextractor.exe")
                
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(file_info.filename) as source, open(dest, "wb") as target:
                shutil.copyfileobj(source, target)

def main():
    if not os.path.exists(BIN_DIR):
        os.makedirs(BIN_DIR)

    # Touch .gitkeep
    with open(os.path.join(BIN_DIR, ".gitkeep"), "w") as f:
        f.write("")

    for name, url in SOURCES.items():
        print(f"\\n--- Processing {name} ---")
        if url.endswith(".exe"):
            dest_exe = os.path.join(BIN_DIR, f"{name}.exe" if not url.endswith(f"{name}.exe") else os.path.basename(url))
            if name == "packager":
                dest_exe = os.path.join(BIN_DIR, "packager.exe")
            download_file(url, dest_exe)
        elif url.endswith(".zip"):
            zip_bytes = download_file(url)
            extract_flat(zip_bytes, BIN_DIR)
            
    print("\\n[+] All binaries downloaded to 'binaries' directory.")

if __name__ == "__main__":
    main()

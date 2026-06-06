import io
import os
import shutil
import sys
import zipfile
import urllib.error
import urllib.request

BIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "binaries"))

IS_WINDOWS = sys.platform == "win32"

ARCH = "win-x64" if IS_WINDOWS else "linux-x64"
BIN_EXT = ".exe" if IS_WINDOWS else ""

SOURCES = {}

if IS_WINDOWS:
    SOURCES = {
        "aria2": "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip",
        "bento4": "https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-microsoft-win32.zip",
        "ccextractor": "https://github.com/CCExtractor/ccextractor/releases/download/v0.96.6/CCExtractor.0.96.6_win_portable.zip",
        "ffmpeg": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",
        "mkvtoolnix": "https://mkvtoolnix.download/windows/releases/99.0/mkvtoolnix-64-bit-99.0.zip",
        "n_m3u8dl-re": "https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.5.1-beta/N_m3u8DL-RE_v0.5.1-beta_win-x64_20251029.zip",
        "packager": "https://github.com/shaka-project/shaka-packager/releases/download/v3.7.2/packager-win-x64.exe",
        "subtitleedit": "https://github.com/SubtitleEdit/subtitleedit/releases/download/4.0.15/SE4015.zip",
        "curl": "https://curl.se/windows/dl-8.19.0_6/curl-8.19.0_6-win64-mingw.zip"
    }
else:
    SOURCES = {
        "aria2": "https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0.tar.xz",
        "bento4": "https://www.bok.net/Bento4/binaries/Bento4-SDK-1-6-0-641.x86_64-unknown-linux.zip",
        "ccextractor": "https://github.com/CCExtractor/ccextractor/releases/download/v0.96.6/ccextractor-hardsubx-x86_64.AppImage",
        "ffmpeg": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz",
        "mkvtoolnix": "https://mkvtoolnix.download/appimage/MKVToolNix_GUI-99.0-x86_64.AppImage",
        "n_m3u8dl-re": "https://github.com/nilaoda/N_m3u8DL-RE/releases/download/v0.5.1-beta/N_m3u8DL-RE_v0.5.1-beta_linux-x64_20251029.tar.gz",
        "packager": "https://github.com/shaka-project/shaka-packager/releases/download/v3.7.2/packager-linux-x64",
        "subtitleedit": None,
        "curl": None
    }


def download_file(url, dest_path=None):
    if url is None:
        return None
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
            elif filename.lower().endswith(('.exe', '.dll') if IS_WINDOWS else ('.exe', '.so')):
                dest = os.path.join(target_dir, os.path.basename(filename))
            else:
                continue

            if os.path.basename(dest).lower() == "ccextractorwinfull.exe":
                dest = os.path.join(target_dir, "ccextractor.exe")

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with z.open(file_info.filename) as source, open(dest, "wb") as target:
                shutil.copyfileobj(source, target)


def extract_tar_xz(stream, target_dir):
    import tarfile
    BIN_NAMES = {'aria2c', 'ffmpeg', 'ffprobe', 'mkvmerge', 'mkvextract', 'mkvinfo', 'mkvpropedit'}
    stream.seek(0)
    with tarfile.open(fileobj=stream, mode="r:xz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                name = os.path.basename(member.name)
                if name in BIN_NAMES or name.lower().endswith(('.exe', '.so')):
                    dest = os.path.join(target_dir, name)
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    with tar.extractfile(member) as source, open(dest, "wb") as target:
                        shutil.copyfileobj(source, target)
                    os.chmod(dest, 0o755)


def main():
    if not os.path.exists(BIN_DIR):
        os.makedirs(BIN_DIR)

    with open(os.path.join(BIN_DIR, ".gitkeep"), "w") as f:
        f.write("")

    for name, url in SOURCES.items():
        if url is None:
            print(f"\n--- {name} --- (skipped, not available for this platform)")
            print(f"Please install via your package manager (e.g. apt install {name})")
            continue

        print(f"\n--- Processing {name} on {sys.platform} ---")

        if name in ("packager",):
            out_name = f"{name}{BIN_EXT}"
            dest_exe = os.path.join(BIN_DIR, out_name)
            download_file(url, dest_exe)
            if not IS_WINDOWS:
                os.chmod(dest_exe, 0o755)
        elif url.endswith(".zip"):
            zip_bytes = download_file(url)
            extract_flat(zip_bytes, BIN_DIR)
            if not IS_WINDOWS:
                for root, dirs, files in os.walk(BIN_DIR):
                    for f in files:
                        fp = os.path.join(root, f)
                        if os.path.isfile(fp) and not f.endswith('.gitkeep'):
                            os.chmod(fp, 0o755)
        elif url.endswith(".tar.xz"):
            stream = download_file(url)
            if stream:
                extract_tar_xz(stream, BIN_DIR)

    print(f"\n[+] All binaries downloaded to '{BIN_DIR}'.")
    print("\n[!] Note: For Linux, you may also install system-wide via your package manager:")
    print("    sudo apt install aria2 ffmpeg mkvtoolnix ccextractor")
    print("    For mp4decrypt: download Bento4 from https://www.bento4.com/")
    print("    For N_m3u8DL-RE and packager, they are handled above.")


if __name__ == "__main__":
    main()

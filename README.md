# 🎬 Vinetrimmer Playready 1.0

A powerful, high-performance CLI engine for downloading and decrypting Widevine and PlayReady DRM-protected content from various streaming platforms. Designed for research and archival purposes.

## 🚀 Key Features

- **Multi-DRM Support**: Seamlessly handles Widevine (L1/L3) and PlayReady (SL2000/SL3000) decryption.
- **High Performance**: Parallelized track downloading and decryption using multi-threading for maximum speed.
- **Service-Oriented Architecture**: Modular service classes for easy platform integration.
- **Track Selection**: Granular control over video quality (up to 4K), audio codecs (AAC, AC3, Atmos), and multi-language subtitles.
- **Atomic Key Vaulting**: Thread-safe SQL storage for decryption keys (KID:KEY) to enable caching and reuse.
- **Advanced Muxing**: Automatic track merging into MKV containers with proper metadata and chapter support.
- **Proxy Integration**: Built-in support for custom HTTP/HTTPS proxies and NordVPN integration.

## 🛠️ Supported Services

| Service | Alias | Platform URL |
| :--- | :--- | :--- |
| **Amazon** | `AMZN` | primevideo.com / amazon.com |
| **Apple TV+** | `ATVP` | tv.apple.com |
| **Canal+** | `CNP` | canalplus.com |
| **Disney+** | `DSNP` | disneyplus.com |
| **France TV** | `FRTV` | france.tv |
| **Hulu** | `HULU` | hulu.com |
| **iTunes** | `iT` | itunes.apple.com |
| **Max** | `MAX` | max.com |
| **NowTV** | `NOW` | nowtv.it |
| **Paramount+** | `PMTP` | paramountplus.com |
| **Peacock** | `PCOK` | peacocktv.com |
| **SkyShowtime** | `SKST` | skyshowtime.com |
| **TimVision** | `TMVS` | timvision.it |

## ⚙️ Requirements

- **Python**: 3.8 or higher.
- **Package Manager**: [Poetry](https://python-poetry.org/) recommended.
- **Core Binaries**: (Placed in `binaries/` or system PATH)
  - `aria2c`: High-speed segmented downloading.
  - `ffmpeg` / `ffprobe`: Media processing and analysis.
  - `mkvmerge`: Container muxing.
  - `mp4decrypt` / `packager`: DRM decryption.
  - `ccextractor`: Captions extraction.
  - `N_m3u8DL-RE`: HLS/DASH manifest handling.

## 🚀 Installation

1. Clone the repository.
2. Install dependencies via Poetry:
   ```bash
   poetry install
   ```
3. Ensure all required binaries are in the `binaries/` directory or your system's `PATH`.

## 📖 Usage

The main command is `vt dl`. You can use it by calling `poetry run vt` or just `vt` if installed.

### Basic Commands

- **List available tracks**:
  ```bash
  vt dl --list AMZN [ASIN]
  ```
- **Download highest quality**:
  ```bash
  vt dl DSNP [EntityID]
  ```
- **Select specific quality and languages**:
  ```bash
  vt dl -q 1080 -al eng,fra -sl eng AMZN [ASIN]
  ```
- **Decrypt using cached keys only (no CDM)**:
  ```bash
  vt dl --cache MAX [TitleID]
  ```

### Quick Access (Windows)

For Windows users, several batch scripts are provided in the root directory for common tasks:
- **Installation**: Run `install.bat` to set up the environment.
- **Service Shortcuts**: Use `download.[Service].bat` (e.g., `download.Amazon.bat`) for quick downloads without manual CLI typing.
- **Help**: Run `help.bat` to see all available commands.
- **Update Binaries**: Run `update_binaries.bat <URL_or_path_to_zip>` to automatically update the contents of the `binaries/` folder from an archive.

### Configuration

Vinetrimmer uses a hierarchical configuration system:
- **Root Config**: `vinetrimmer.yml` defines global settings (decrypter, paths, templates, proxy).
- **Service Configs**: `vinetrimmer/config/services/*.yml` define platform-specific endpoints and certificates.
- **Cookies**: Place Netscape-formatted cookies in `vinetrimmer/cookies/[service]/[profile].txt`.
- **Devices**: CDM device files (WVD/PRD) go into `vinetrimmer/devices/`.

## 🔧 Maintenance Scripts

A collection of utility scripts is provided in the `scripts/` directory:

- `update_binaries.py`: Script to update and extract new core binaries from a ZIP file (URL or local path) into the `binaries/` directory. Example: `python scripts/update_binaries.py <URL>`
- `AddKeysToKeyVault.py`: Batch add `KID:KEY` pairs to the SQL database.
- `MergeKeyStores.py`: Merge multiple key storage databases.
- `ParsePSSH.py`: Extract metadata and KIDs from Widevine PSSH boxes.
- `MakeWVD.py`: Convert folder-based CDM data into Vinetrimmer WVD structs.
- `VMPBlobGen.py`: Generate VMP (Verified Media Path) blobs for Chrome CDM.
- `ParseClientID.py`: Inspect Widevine Client ID blobs.

## 🎬 Disclaimer

This project is intended for educational purposes and interoperability research. The authors do not encourage or condone the use of this software for piracy or any illegal activities. Users are responsible for complying with the terms of service of any streaming platforms they access.



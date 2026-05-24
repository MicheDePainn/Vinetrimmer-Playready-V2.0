# Vinetrimmer Playready 2.0

![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?logo=windows&logoColor=white)
![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-44CC11)

A powerful, high-performance CLI engine for downloading and decrypting Widevine and PlayReady DRM-protected content from various streaming platforms. Designed for research and archival purposes.

## Table of Contents
- [Key Features](#key-features)
- [Supported Services](#supported-services)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Maintenance Scripts](#maintenance-scripts)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)

---

## Key Features

- **PlayReady & Widevine Support**: Seamlessly handles PlayReady (SL2000/SL3000) and Widevine (L1/L3) decryption.
- **High Performance**: Parallelized track downloading and decryption using multi-threading for maximum speed.
- **Service-Oriented Architecture**: Modular service classes for easy platform integration.
- **Track Selection**: Granular control over video quality (up to 4K), audio codecs (AAC, AC3, Atmos), and multi-language subtitles.
- **Atomic Key Vaulting**: Thread-safe SQL storage for decryption keys (KID:KEY) to enable caching and reuse.
- **Advanced Muxing**: Automatic track merging into MKV containers with proper metadata and chapter support.
- **Proxy Integration**: Built-in support for custom HTTP/HTTPS proxies and NordVPN integration.

---

## Supported Services

| Service | Alias | Platform URL | Risk Level / Ban Policy |
| :--- | :--- | :--- | :--- |
| **Amazon** | `AMZN` | primevideo.com / amazon.com | Instant Account Ban |
| **Apple TV+** | `ATVP` | tv.apple.com | Instant Account Ban |
| **iTunes** | `iT` | itunes.apple.com | Instant Account Ban |
| **Canal+** | `CNP` | canalplus.com | Temporary IP Ban / Warning |
| **Disney+** | `DSNP` | disneyplus.com | Temporary IP Ban / Warning |
| **NowTV** | `NOW` | nowtv.it | Temporary IP Ban / Warning |
| **SkyShowtime** | `SKST` | skyshowtime.com | Temporary IP Ban / Warning |
| **TimVision** | `TMVS` | timvision.it | Temporary IP Ban / Warning |
| **Hulu** | `HULU` | hulu.com | Low / Moderate Risk |
| **Max** | `MAX` | max.com | Low / Moderate Risk |
| **Paramount+** | `PMTP` | paramountplus.com | Low / Moderate Risk |
| **Peacock** | `PCOK` | peacocktv.com | Low / Moderate Risk |
| **France TV** | `FRTV` | france.tv | Safe / No Risk |

---

## Requirements

> [!IMPORTANT]  
> This project is currently compatible with **Windows environments only**.

- **Operating System**: Windows 10 / 11
- **Python**: 3.10 - 3.13
- **Package Manager**: [Poetry](https://python-poetry.org/) recommended.
- **Core Binaries**: (Must be placed in `binaries/` or added to system PATH via `install_binaries.py`)
  - `aria2c`: High-speed segmented downloading.
  - `ffmpeg` / `ffprobe`: Media processing and analysis.
  - `mkvmerge`: Container muxing.
  - `mp4decrypt` / `packager`: DRM decryption.
  - `ccextractor`: Captions extraction.
  - `N_m3u8DL-RE`: HLS/DASH manifest handling.

---

## Installation

1. Clone or download the repository.
2. Ensure you have the **Microsoft Visual C++ Redistributable** installed.
3. Double-click on `install.bat`.
   
   *Alternatively, run manually via command line:*
   ```bash
   python -m pip install poetry
   poetry install
   python install_binaries.py
   ```

---

## Usage

The main command engine is `vt dl`. You can run it by calling `poetry run vt dl`.

### Basic Commands

- **List available tracks**:
  ```bash
  poetry run vt dl --list AMZN [ASIN]
  ```
- **Download highest quality**:
  ```bash
  poetry run vt dl DSNP [EntityID]
  ```
- **Select specific quality and languages**:
  ```bash
  poetry run vt dl -q 1080 -al eng,fra -sl eng AMZN [ASIN]
  ```
- **Decrypt using cached keys only (no CDM required)**:
  ```bash
  poetry run vt dl --cache MAX [TitleID]
  ```

### Quick Access (Windows Shortcuts)

Several batch scripts are provided in the root directory for common tasks:
- **Service Shortcuts**: Use `download.[Service].bat` (e.g., `download.Amazon.bat`) for quick downloads without manual CLI typing.
- **Help**: Run `help.bat` to see all available commands and flags.

### Configuration

Vinetrimmer uses a hierarchical configuration system:
- **Root Config**: `vinetrimmer\vinetrimmer.yml` defines global settings (CDMs, paths, credentials, proxy).
- **Service Configs**: `vinetrimmer\config\services\*.yml` define platform-specific endpoints and options.
- **Cookies**: Place Netscape-formatted cookies in `vinetrimmer\cookies\[service]\default.txt`.
- **Devices (CDMs)**: CDM device files (PRD, bgroupcert/zgpriv, etc.) go into `vinetrimmer\devices\`.

See `How.to.use.txt` for more detailed instructions on cookies, credentials, and CDM setup.

---

## Maintenance Scripts

A collection of utility scripts is provided in the `scripts/` directory:

- `AddKeysToKeyVault.py`: Batch add `KID:KEY` pairs to the SQL database.
- `MergeKeyStores.py`: Merge multiple key storage databases.
- `ParsePSSH.py`: Extract metadata and KIDs from Widevine/PlayReady PSSH boxes.
- `MakeWVD.py`: Convert folder-based CDM data into Vinetrimmer WVD structs.
- `VMPBlobGen.py`: Generate VMP (Verified Media Path) blobs for Chrome CDM.
- `ParseClientID.py`: Inspect Widevine Client ID blobs.

---

## Roadmap

- [ ] **Strict Pydantic Validation**: Replacing standard dictionaries with strictly typed models for configurations and API responses to enhance reliability.
- [ ] **Asynchronous Architecture**: Migrating the core HTTP engine to `asyncio` to drastically increase network execution performance.

---

## Disclaimer

This project is intended for educational purposes and interoperability research. The authors do not encourage or condone the use of this software for piracy or any illegal activities. Users are responsible for complying with the terms of service of any streaming platforms they access.

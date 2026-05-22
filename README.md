# Vinetrimmer Playready 2.0

A powerful, high-performance CLI engine for downloading and decrypting Widevine and PlayReady DRM-protected content from various streaming platforms. Designed for research and archival purposes.

## Key Features

- **PlayReady & Widevine Support**: Seamlessly handles PlayReady (SL2000/SL3000) and Widevine (L1/L3) decryption.
- **High Performance**: Parallelized track downloading and decryption using multi-threading for maximum speed.
- **Service-Oriented Architecture**: Modular service classes for easy platform integration.
- **Track Selection**: Granular control over video quality (up to 4K), audio codecs (AAC, AC3, Atmos), and multi-language subtitles.
- **Atomic Key Vaulting**: Thread-safe SQL storage for decryption keys (KID:KEY) to enable caching and reuse.
- **Advanced Muxing**: Automatic track merging into MKV containers with proper metadata and chapter support.
- **Proxy Integration**: Built-in support for custom HTTP/HTTPS proxies and NordVPN integration.

## Supported Services

| Service | Alias | Platform URL | Dégats (Bans) |
| :--- | :--- | :--- | :--- |
| **Amazon** | `AMZN` | primevideo.com / amazon.com | Ban de compte (Rapide) |
| **Apple TV+** | `ATVP` | tv.apple.com | Ban de compte (Rapide) |
| **iTunes** | `iT` | itunes.apple.com | Ban de compte (Rapide) |
| **Canal+** | `CNP` | canalplus.com | Ban IP temporaire / Avertissement |
| **Disney+** | `DSNP` | disneyplus.com | Ban IP temporaire / Avertissement |
| **NowTV** | `NOW` | nowtv.it | Ban IP temporaire / Avertissement |
| **SkyShowtime** | `SKST` | skyshowtime.com | Ban IP temporaire / Avertissement |
| **TimVision** | `TMVS` | timvision.it | Ban IP temporaire / Avertissement |
| **Hulu** | `HULU` | hulu.com | Faible / Modéré |
| **Max** | `MAX` | max.com | Faible / Modéré |
| **Paramount+** | `PMTP` | paramountplus.com | Faible / Modéré |
| **Peacock** | `PCOK` | peacocktv.com | Faible / Modéré |
| **France TV** | `FRTV` | france.tv | Aucun |

## Requirements

- **Python**: 3.10 - 3.14 recommended.
- **Package Manager**: [Poetry](https://python-poetry.org/) recommended.
- **Core Binaries**: (Placed in `binaries/` or system PATH via `install_binaries.py`)
  - `aria2c`: High-speed segmented downloading.
  - `ffmpeg` / `ffprobe`: Media processing and analysis.
  - `mkvmerge`: Container muxing.
  - `mp4decrypt` / `packager`: DRM decryption.
  - `ccextractor`: Captions extraction.
  - `N_m3u8DL-RE`: HLS/DASH manifest handling.

## Installation

1. Clone or download the repository.
2. Ensure you have Microsoft Visual C++ Redistributable installed.
3. Windows users: Double click on `install.bat`.
   *Alternatively, run manually:*
   ```bash
   python -m pip install poetry
   poetry install
   python install_binaries.py
   ```

## Usage

The main command is `vt dl`. You can use it by calling `poetry run vt dl`.

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
- **Decrypt using cached keys only (no CDM)**:
  ```bash
  poetry run vt dl --cache MAX [TitleID]
  ```

### Quick Access (Windows)

For Windows users, several batch scripts are provided in the root directory for common tasks:
- **Service Shortcuts**: Use `download.[Service].bat` (e.g., `download.Amazon.bat`) for quick downloads without manual CLI typing.
- **Help**: Run `help.bat` to see all available commands.

### Configuration

Vinetrimmer uses a hierarchical configuration system:
- **Root Config**: `vinetrimmer\vinetrimmer.yml` defines global settings (CDMs, paths, credentials, proxy).
- **Service Configs**: `vinetrimmer\config\services\*.yml` define platform-specific endpoints and options.
- **Cookies**: Place Netscape-formatted cookies in `vinetrimmer\cookies\[service]\default.txt`.
- **Devices (CDMs)**: CDM device files (PRD, bgroupcert/zgpriv, etc.) go into `vinetrimmer\devices\`.

See `How.to.use.txt` for more detailed instructions on cookies, credentials, and CDM setup.

## Maintenance Scripts

A collection of utility scripts is provided in the `scripts/` directory:

- `AddKeysToKeyVault.py`: Batch add `KID:KEY` pairs to the SQL database.
- `MergeKeyStores.py`: Merge multiple key storage databases.
- `ParsePSSH.py`: Extract metadata and KIDs from Widevine/PlayReady PSSH boxes.
- `MakeWVD.py`: Convert folder-based CDM data into Vinetrimmer WVD structs.
- `VMPBlobGen.py`: Generate VMP (Verified Media Path) blobs for Chrome CDM.
- `ParseClientID.py`: Inspect Widevine Client ID blobs.

## Roadmap (Améliorations Prévues)

- [ ] **Validation forte avec Pydantic** : Remplacement des dictionnaires par des modèles typés pour les configurations et réponses API.
- [ ] **Asynchronisme** : Migration vers `asyncio` pour les requêtes HTTP afin d'améliorer considérablement les performances.

## Disclaimer

This project is intended for educational purposes and interoperability research. The authors do not encourage or condone the use of this software for piracy or any illegal activities. Users are responsible for complying with the terms of service of any streaming platforms they access.
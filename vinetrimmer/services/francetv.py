import base64
import glob
import os
import re
import shutil
import subprocess
import types
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import click
from langcodes import Language

from vinetrimmer.config import directories
from vinetrimmer.objects import Title, Tracks, AudioTrack, TextTrack, MenuTrack
from vinetrimmer.services.BaseService import BaseService
from vinetrimmer.utils.io import get_m3u8dl_exe


class FranceTV(BaseService):

    ALIASES = ["FRTV", "FranceTV", "francetv", "france.tv", "ftv"]
    GEOFENCE = ["fr"]
    TITLE_RE = [
        r"https?://(?:www\.)?france\.tv/[^/]+/[^/]+/(?P<id>[^/]+)\.html",
        r"https?://(?:www\.)?france\.tv/[^/]+/(?P<id>[^/]+)/?",
        r"https?://(?:www|mobile|france3-regions)\.france(?:tv)?info\.fr/.*",
    ]

    UUID_REGEX = re.compile(r"(?i)^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$")
    UUID_SEARCH_REGEX = re.compile(r"(?i)([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
    
    PLAYER_WRAPPER_REGEX = re.compile(r'data-cy="francetv-player-wrapper"[^>]*id="([^"]+)"')
    DATA_ID_REGEX = re.compile(r'(?:data-id|<figure[^<]+\bid)=["\']([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})["\']', re.IGNORECASE)
    NEXT_VIDEO_ID_REGEX = re.compile(r'"videoId"\s*:\s*"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"', re.IGNORECASE)
    NEXTJS_OPTIONS_ID_REGEX = re.compile(r'\\?"options\\?"\s*:\s*\{[^}]*\\?"id\\?"\s*:\s*\\?"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\\?"', re.IGNORECASE)
    VIDEO_ID_JSON_REGEX = re.compile(r'"id"\s*:\s*"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})"', re.IGNORECASE)

    @staticmethod
    @click.command(name="FranceTV", short_help="France.tv (FRTV)")
    @click.argument("title", type=str)
    @click.option("--movie", is_flag=True, default=False, help="Is a movie.")
    @click.pass_context
    def cli(ctx, title, movie):
        return FranceTV(ctx, title, movie)

    def __init__(self, ctx, title, movie):
        super().__init__(ctx)
        self.original_title = title
        self.title_match = self.parse_title(ctx, title)
        self.movie = movie
        
        self.video_ids = []
        self._drm_token_cache = {}
        self._lock = Lock()
        self.manifest_url = None
        
        self.configure()

    def configure(self):
        self.session.headers.update({"Referer": "https://www.france.tv/"})
        
        uuid_match = self.UUID_REGEX.search(self.original_title.strip())
        if uuid_match:
            self.video_ids = [uuid_match.group(1)]
            self.log.info(f" + Found Video ID directly: {self.video_ids[0]}")
            return

        url = self.original_title if self.original_title.startswith("http") else f"https://www.france.tv/{self.original_title}.html"
        self.log.info(f"Fetching webpage: {url}")
        
        try:
            res = self.session.get(url, timeout=10)
            res.raise_for_status()
            html_text = res.text
            
            if not html_text or not html_text.strip():
                raise Exception("Empty page content")
        except Exception as e:
            self.log.info(f" - Failed to fetch webpage: {e}")
            raise self.log.exit(f" - Failed to fetch webpage: {e}")
        
        primary_ids = []
        
        primary_ids.extend(self.PLAYER_WRAPPER_REGEX.findall(html_text))
        primary_ids.extend(self.DATA_ID_REGEX.findall(html_text))
        primary_ids.extend(self.NEXTJS_OPTIONS_ID_REGEX.findall(html_text))
        primary_ids.extend(self.NEXT_VIDEO_ID_REGEX.findall(html_text))
        primary_ids.extend(self.VIDEO_ID_JSON_REGEX.findall(html_text))
        
        all_ids = self.UUID_SEARCH_REGEX.findall(html_text)
        combined_ids = primary_ids + all_ids
        
        self.video_ids = []
        seen = set()
        for vid in combined_ids:
            if vid not in seen and self.UUID_SEARCH_REGEX.match(vid):
                self.video_ids.append(vid)
                seen.add(vid)
        
        if not self.video_ids:
            raise self.log.exit(" - Could not find any Video IDs on webpage. Please provide the video ID directly.")
        
        self.log.info(f" + Found {len(self.video_ids)} potential Video ID(s)")

    def get_titles(self):
        titles = []

        def get_title_metadata(vid):
            url = self.config["endpoints"]["video"].format(video_id=vid)
            params = {
                "device_type": "desktop",
                "browser": "chrome",
                "domain": "www.france.tv",
                "capabilities": "drm",
                "player_version": "5.140.0"
            }
            try:
                res = self.session.get(url, params=params, timeout=10)
                if res.status_code != 200:
                    return None
                
                data = res.json()
                if data.get("code") not in (None, 200):
                    return None

                meta = data.get("meta", {})
                title_str = meta.get("title", "Unknown Title")
                pre_title = meta.get("pre_title", "")
                additional_title = meta.get("additional_title")
                
                season, episode = 0, 0
                if pre_title:
                    m = re.search(r'S(\d+)\s*E(\d+)', pre_title, re.IGNORECASE)
                    if m:
                        season = int(m.group(1))
                        episode = int(m.group(2))
                
                is_movie = self.movie or (season == 0 and episode == 0)
                
                return Title(
                    id_=vid,
                    type_=Title.Types.MOVIE if is_movie else Title.Types.TV,
                    name=title_str,
                    season=None if is_movie else season,
                    episode=None if is_movie else episode,
                    episode_name=None if is_movie else additional_title,
                    year=None,
                    original_lang="fr",
                    source=self.ALIASES[0],
                    service_data=data
                )
            except Exception as e:
                self.log.debug(f"Failed to fetch metadata for {vid}: {e}")
                return None

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_title_metadata, vid) for vid in self.video_ids]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    titles.append(result)
        
        if not titles:
            raise self.log.exit(" - No valid titles could be retrieved from the found IDs.")
            
        return titles

    def get_chapters(self, title):
        chapters = []
        video_data = title.service_data.get("video", {})
        
        events = {
            "previously": "Previously",
            "skip_intro": "Intro",
            "coming_next": "Next",
            "closing_credits": "Credits"
        }

        chapter_times = []
        
        for key, name in events.items():
            data = video_data.get(key)
            if data and isinstance(data, dict):
                timecode = data.get("timecode")
                if isinstance(timecode, (int, float)):
                    chapter_times.append((timecode, name))
                    duration = data.get("duration")
                    if isinstance(duration, (int, float)):
                        chapter_times.append((timecode + duration, f"{name} End"))

        if not chapter_times:
            return chapters

        chapter_times = sorted(list(set(chapter_times)), key=lambda x: x[0])

        for number, (timecode, title_name) in enumerate(chapter_times, start=1):
            chapters.append(
                MenuTrack(
                    number=number,
                    title=title_name,
                    timecode=MenuTrack.format_duration(timecode)
                )
            )

        return chapters

    def get_tracks(self, title):
        video_data = title.service_data.get("video", {})
        video_formats = video_data.get("formats", [])
        
        global_token_url = video_data.get("token", {}).get("akamai")
        global_url = video_data.get("url")
        dash_formats = [f for f in video_formats if f.get("format") == "dash"]
        manifest_urls = []
        
        def fetch_tokenized_url(base_url, token_url_):
            try:
                self.log.debug(f"Fetching tokenized URL from: {token_url_} for {base_url}")
                res = self.session.get(token_url_, params={"format": "json", "url": base_url}, timeout=10)
                return res.json().get("url", base_url)
            except Exception as e:
                self.log.debug(f"Failed to fetch tokenized URL: {e}")
                return base_url

        if not dash_formats and global_url:
            url = fetch_tokenized_url(global_url, global_token_url) if global_token_url else global_url
            manifest_urls.append(url)
        else:
            for f in dash_formats:
                url = f.get("url")
                token_url = f.get("token") or global_token_url
                if url:
                    manifest_urls.append(fetch_tokenized_url(url, token_url) if token_url else url)
            
        if not manifest_urls:
            raise self.log.exit(" - No DASH manifest found for this video.")
            
        self.manifest_url = next((u for u in manifest_urls if "france-domtom" not in u), manifest_urls[0])
        self.log.info(f" + Manifest URL: {self.manifest_url}")
            
        self._fetch_drm_token(title.id)

        tracks = Tracks.from_mpd(url=self.manifest_url, session=self.session, source=self.ALIASES[0])
        
        for track in tracks:
            track.needs_proxy = True
            
            try:
                lang_str = str(track.language).lower()
                if lang_str == "qsm":
                    track.language = Language.get("fr")
                    if isinstance(track, TextTrack):
                        track.sdh = True
                elif lang_str in ["qtz", "qad"]:
                    track.language = Language.get("fr")
                    if isinstance(track, AudioTrack):
                        track.descriptive = True
            except Exception as e:
                self.log.debug(f"Language conversion failed for {track.id}: {e}")
            
            if isinstance(track, TextTrack):
                track.download = types.MethodType(self._custom_text_track_download, track)
                
        return tracks

    def _custom_text_track_download(self, track, out, name=None, headers=None, proxy=None):
        tmp = os.path.join(out, f"tmp_sub_{track.id}")
        os.makedirs(tmp, exist_ok=True)
        
        re_exe = get_m3u8dl_exe()
        if not re_exe:
            self.log.warning(" - N_m3u8DL-RE not found, falling back to standard download")
            return track.__class__.__bases__[0].download(track, out, name, headers, proxy)

        cmd = [
            re_exe, self.manifest_url,
            "--sub-only",
            "--auto-select",
            "--sub-format", "SRT",
            "--save-dir", tmp,
            "--save-name", "sub",
            "--log-level", "OFF"
        ]
        
        if proxy:
            cmd.extend(["--proxy", proxy])

        for k, v in self.session.headers.items():
            cmd.extend(["-H", f"{k}: {v}"])
        
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            srt_files = glob.glob(os.path.join(tmp, "*.srt"))
            if srt_files:
                srt_files.sort(key=os.path.getsize, reverse=True)
                save_path = os.path.join(out, (name or "{type}_{id}_{enc}").format(
                    type="TextTrack", id=track.id, enc="enc" if track.encrypted else "dec") + ".srt")
                shutil.move(srt_files[0], save_path)
                track._location, track.codec = save_path, "srt"
                return save_path
        except Exception as e:
            self.log.warning(f" - N_m3u8DL-RE failed: {e}")
        finally:
            if os.path.exists(tmp):
                shutil.rmtree(tmp, ignore_errors=True)
        
        return track.__class__.__bases__[0].download(track, out, name, headers, proxy)

    def _fetch_drm_token(self, video_id):
        with self._lock:
            if video_id in self._drm_token_cache:
                return self._drm_token_cache[video_id]

            try:
                res = self.session.post(
                    self.config["endpoints"]["drm_token"],
                    params={"v": "2"},
                    json={"id": video_id, "drm_type": "playready", "license_type": "online"},
                    timeout=10
                )
                if res.status_code == 200:
                    token = res.json().get("token")
                    if token:
                        self._drm_token_cache[video_id] = token
                        return token
                else:
                    self.log.debug(f"DRM Token API status: {res.status_code}")
            except Exception as e:
                self.log.warning(f" - Failed to fetch DRM token: {e}")

            return None

    def license(self, challenge, title, track, **kwargs):
        token = self._fetch_drm_token(title.id)
        if not token:
            raise self.log.exit(" - Failed to obtain DRM token for license request.")

        headers = {
            "nv-authorizations": token,
            "Content-Type": "text/xml",
        }

        try:
            res = self.session.post(
                self.config["endpoints"]["license"],
                headers=headers,
                data=challenge,
                timeout=10
            )
            
            if res.status_code != 200:
                raise self.log.exit(f" - License request failed: HTTP {res.status_code} - {res.text}")
                
            return base64.b64encode(res.content).decode()
        except Exception as e:
            raise self.log.exit(f" - License request failed with exception: {e}")
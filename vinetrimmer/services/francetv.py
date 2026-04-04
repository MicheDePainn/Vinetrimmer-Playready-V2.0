import base64
import re

import click
from langcodes import Language

from vinetrimmer.objects import Title, Tracks
from vinetrimmer.services.BaseService import BaseService


class FranceTV(BaseService):
    """
    France.tv
    """

    ALIASES = ["FRTV", "FranceTV", "francetv", "france.tv", "ftv"]
    GEOFENCE = ["fr"]
    TITLE_RE = [
        r"https?://(?:www\.)?france\.tv/[^/]+/[^/]+/(?P<id>[^/]+)\.html",
        r"https?://(?:www\.)?france\.tv/[^/]+/(?P<id>[^/]+)/?",
    ]

    UUID_REGEX = re.compile(r"(?i)([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})")
    PLAYER_WRAPPER_REGEX = re.compile(r'data-cy="francetv-player-wrapper"[^>]*id="([^"]+)"')
    DATA_ID_REGEX = re.compile(r'data-id="([^"]+)"')
    NEXT_VIDEO_ID_REGEX = re.compile(r'"videoId"\s*:\s*"([^"]+)"')

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
        self.drm_token = None
        
        self.configure()

    def configure(self):
        self.session.headers.update({"Referer": "https://www.france.tv/"})
        
        if self.UUID_REGEX.match(self.title):
            self.video_ids = [self.title]
            self.log.info(f" + Found Video ID directly: {self.video_ids[0]}")
            return

        url = self.original_title if self.original_title.startswith("http") else f"https://www.france.tv/{self.title}.html"
        self.log.info(f"Fetching webpage: {url}")
        res = self.session.get(url)
        
        primary_ids = []
        primary_ids.extend(self.PLAYER_WRAPPER_REGEX.findall(res.text))
        primary_ids.extend(self.DATA_ID_REGEX.findall(res.text))
        primary_ids.extend(self.NEXT_VIDEO_ID_REGEX.findall(res.text))
        
        all_ids = self.UUID_REGEX.findall(res.text)
        
        combined_ids = primary_ids + all_ids
        self.video_ids = list(dict.fromkeys([vid for vid in combined_ids if self.UUID_REGEX.match(vid)]))
        
        if not self.video_ids:
            raise self.log.exit(" - Could not find any Video IDs on webpage. Please provide the video ID directly.")
        
        self.log.info(f" + Found {len(self.video_ids)} potential Video ID(s)")

    def get_titles(self):
        titles = []
        for vid in self.video_ids:
            url = self.config["endpoints"]["video"].format(video_id=vid)
            params = {
                "device_type": "desktop",
                "browser": "chrome",
                "domain": "www.france.tv",
                "capabilities": "drm",
                "player_version": "5.140.0"
            }
            
            try:
                res = self.session.get(url, params=params)
                if res.status_code != 200:
                    continue
                
                data = res.json()
                if data.get("code") not in (None, 200):
                    continue

                meta = data.get("meta", {})
                title_str = meta.get("title", "Unknown Title")
                pre_title = meta.get("pre_title", "")
                additional_title = meta.get("additional_title")
                
                season, episode = 0, 0
                if pre_title:
                    m = re.search(r'S(\d+)\s*E(\d+)', pre_title)
                    if m:
                        season = int(m.group(1))
                        episode = int(m.group(2))
                
                is_movie = self.movie or episode == 0
                
                titles.append(Title(
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
                ))
            except Exception:
                pass
        
        if not titles:
            raise self.log.exit(" - No valid titles could be retrieved from the found IDs.")
            
        return titles

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
                res = self.session.get(token_url_, params={"format": "json", "url": base_url})
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
            
        manifest_url = next((u for u in manifest_urls if "france-domtom" not in u), manifest_urls[0])
        self.log.info(f" + Manifest URL: {manifest_url}")
            
        self._fetch_drm_token(title.id)

        tracks = Tracks.from_mpd(url=manifest_url, session=self.session, source=self.ALIASES[0])
        
        for track in tracks:
            track.needs_proxy = True
            
            # Conversion des codes langues non-standards de France.tv
            try:
                lang_str = str(track.language).lower()
                if lang_str in ["qsm", "qtz", "qad"]:
                    track.language = Language.get("fr")
                    # Ajout d'un nom de piste propre pour mkvmerge si besoin
                    if lang_str == "qsm" and track.__class__.__name__ == "TextTrack":
                        track.name = "Sourds et malentendants"
                    elif lang_str in ["qtz", "qad"] and track.__class__.__name__ == "AudioTrack":
                        track.name = "Audiodescription"
            except Exception:
                pass
                
        return tracks

    def _fetch_drm_token(self, video_id):
        try:
            res = self.session.post(
                self.config["endpoints"]["drm_token"],
                params={"v": "2"},
                json={"id": video_id, "drm_type": "playready", "license_type": "online"}
            )
            if res.status_code == 200:
                self.drm_token = res.json().get("token")
            else:
                self.log.debug(f"DRM Token API status: {res.status_code}")
        except Exception as e:
            self.log.warning(f" - Failed to fetch DRM token: {e}")

    def license(self, challenge, title, track, **kwargs):
        self._fetch_drm_token(title.id)

        headers = {
            "nv-authorizations": self.drm_token,
            "Content-Type": "text/xml",
        }
        
        res = self.session.post(
            self.config["endpoints"]["license"],
            headers=headers,
            data=challenge
        )
        
        if res.status_code != 200:
            raise self.log.exit(f" - License request failed: HTTP {res.status_code} - {res.text}")
            
        return base64.b64encode(res.content).decode()
import base64
import json
import re

import click
import requests

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
        
        self.video_id = []
        self.drm_token = None
        
        self.configure()

    def configure(self):
        self.session.headers.update({"Referer": "https://www.france.tv/"})
        if re.match(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", self.title):
            self.video_id = [self.title]
        else:
            url = self.original_title if self.original_title.startswith("http") else f"https://www.france.tv/{self.title}.html"
            self.log.info(f"Fetching webpage: {url}")
            res = self.session.get(url)
            
            # Try to find videoIds in Next.js data and other attributes
            video_ids = re.findall(r'\"(?:videoId|src|id)\"\s*:\s*\"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\"', res.text)
            if not video_ids:
                video_ids = re.findall(r'data-id\s*=\s*\"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})\"', res.text)
            
            if not video_ids:
                # Fallback to any UUIDs found
                video_ids = re.findall(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', res.text)
            
            if video_ids:
                self.video_id = list(dict.fromkeys(video_ids))
            else:
                raise self.log.exit(" - Could not find Video ID on webpage. Please provide the video ID directly.")
        
        self.log.info(f" + Found {len(self.video_id)} Video ID(s)")

    def get_titles(self):
        titles = []
        for vid in self.video_id:
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
                if res.status_code != 200: continue
                
                data = res.json()
                if "code" in data and data.get("code") != 200: continue

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
                
                if episode > 0 or self.movie == False:
                    titles.append(Title(
                        id_=vid,
                        type_=Title.Types.TV if episode > 0 else Title.Types.MOVIE,
                        name=title_str,
                        season=season,
                        episode=episode,
                        episode_name=additional_title,
                        original_lang="fr",
                        source=self.ALIASES[0],
                        service_data=data
                    ))
                else:
                    titles.append(Title(
                        id_=vid,
                        type_=Title.Types.MOVIE,
                        name=title_str,
                        year=None,
                        original_lang="fr",
                        source=self.ALIASES[0],
                        service_data=data
                    ))
            except Exception: pass
                
        if not titles:
            raise self.log.exit(" - No titles could be retrieved.")
        return titles

    def get_tracks(self, title):
        video_data = title.service_data
        video_obj = video_data.get("video", {})
        video_formats = video_obj.get("formats", [])
        
        # Check for global tokenization
        global_token_url = video_obj.get("token", {}).get("akamai")
        global_url = video_obj.get("url")
        
        dash_formats = [f for f in video_formats if f.get("format") == "dash"]
        manifest_urls = []
        
        if not dash_formats:
            url = global_url
            if url:
                token_url = global_token_url
                if token_url:
                    try:
                        self.log.debug(f"Fetching tokenized URL from global: {token_url} for {url}")
                        res = self.session.get(token_url, params={"format": "json", "url": url})
                        url = res.json().get("url", url)
                    except Exception as e:
                        self.log.debug(f"Failed to fetch global tokenized URL: {e}")
                manifest_urls.append(url)
        else:
            for f in dash_formats:
                url = f.get("url")
                token_url = f.get("token") or global_token_url
                if token_url:
                    try:
                        self.log.debug(f"Fetching tokenized URL from: {token_url} for {url}")
                        res = self.session.get(token_url, params={"format": "json", "url": url})
                        url = res.json().get("url", url)
                    except Exception as e:
                        self.log.debug(f"Failed to fetch tokenized URL: {e}")
                if url: manifest_urls.append(url)
            
        if not manifest_urls:
            raise self.log.exit(" - No DASH manifest found for this video.")
            
        # Prefer mainland France manifest if possible
        manifest_url = next((u for u in manifest_urls if "france-domtom" not in u), manifest_urls[0])
        self.log.info(f" + Manifest URL: {manifest_url}")
            
        # Get DRM token
        try:
            token_url = self.config["endpoints"]["drm_token"]
            res = self.session.post(
                token_url,
                params={"v": "2"},
                json={
                    "id": title.id,
                    "drm_type": "playready",
                    "license_type": "online"
                }
            )
            self.log.debug(f"DRM Token status: {res.status_code}")
            if res.status_code == 200:
                self.drm_token = res.json().get("token")
        except Exception as e:
            self.log.warning(f" - Failed to fetch DRM token: {e}")

        tracks = Tracks.from_mpd(url=manifest_url, session=self.session, source=self.ALIASES[0])
        for track in tracks:
            track.needs_proxy = True
        return tracks

    def license(self, challenge, title, track, **kwargs):
        if not self.drm_token:
            try:
                res = self.session.post(
                    self.config["endpoints"]["drm_token"],
                    params={"v": "2"},
                    json={
                        "id": title.id,
                        "drm_type": "playready",
                        "license_type": "online"
                    }
                )
                if res.status_code == 200:
                    self.drm_token = res.json().get("token")
            except Exception as e:
                self.log.debug(f"Failed to fetch DRM token in license: {e}")

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

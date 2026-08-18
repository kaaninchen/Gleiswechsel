import json
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class DiscordConfig:
    token: str
    server: int
    vc: int
    lang: str
    formatting: str
    emojis: bool

@dataclass
class ConnectionsConfig:
    stations: list[str]
    IDs: list[str]
    blacklist: list[str]
    min_duration: int
    timezone: str
    max_wait_time: Optional[int] = None
    max_duration: Optional[int] = None

@dataclass
class AnnouncementConfig:
    text_announcements: bool
    voice_announcements: bool

@dataclass
class HttpConfig:
    user_agent: str

@dataclass
class Config:
    discord: DiscordConfig
    connections: ConnectionsConfig
    announcements: AnnouncementConfig
    http: HttpConfig

def _load_config() -> Config:
    with open("config.json", "r") as file:
        raw = json.load(file)
    
    return Config(
        discord=DiscordConfig(**raw["discord"]),
        connections=ConnectionsConfig(**raw["connections"]),
        announcements=AnnouncementConfig(**raw["announcements"]),
        http=HttpConfig(**raw["http"]),
    )

config = _load_config()
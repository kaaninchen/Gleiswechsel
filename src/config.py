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
    blacklist: list[str]
    min_duration: int
    max_wait_time: int
    timezone: str
    max_duration: Optional[int] = None

@dataclass
class VoiceAnnouncementConfig:
    enabled: bool
    end_stations: dict[str, str]
    stops: dict[str, str]

@dataclass
class AnnouncementConfig:
    enabled: bool
    voice: list[VoiceAnnouncementConfig]

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
        announcements=AnnouncementConfig(
            enabled=raw["announcements"]["enabled"],
            voice=[VoiceAnnouncementConfig(**v) for v in raw["announcements"]["voice"]],
        ),
        http=HttpConfig(**raw["http"]),
    )

config = _load_config()
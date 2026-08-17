import discord
import random

from src.utils import get_operator_metadata, get_next_station, format_via_list, format_stop_list
from src.dc.helpers import format_timestamp_to_dc

def build_embed_footer(mode: str, slogans):
    footer_notice = f"Data provided by https://transitous.org • mode: {mode}"
    icon = "https://raw.githubusercontent.com/kaaninchen/Gleiswechsel/refs/heads/main/src/data/assets/transitous-logo.png"

    if slogans is not None:
        footer_text = f"{random.choice(slogans)} • {footer_notice}"
    else:
        footer_text = footer_notice

    return {
        "text": footer_text,
        "icon": icon
    }

def build_info_embed() -> discord.Embed:
    from src.dc.handlers import trip

    agency = trip["agency"]
    metadata = get_operator_metadata(agency, trip["route_color"])
    departure = format_timestamp_to_dc(trip["departure"])
    arrival = format_timestamp_to_dc(trip["arrival"])

    embed = discord.Embed(
        title = trip["long_name"],
        description=f"Abfahrt von {trip["station"]} um {departure}. Ankunft um {arrival}",
        color = metadata["color"]
    )

    stops = trip["stops"]

    next_stop = get_next_station(trip["stops"], trip["from"])
    next_stop_station = None
    if next_stop:
        next_stop_station = next_stop.get("name")

    via = format_via_list(stops)

    if via:
        embed.add_field(name="Über", value=via, inline=False)
    if next_stop:
        embed.add_field(name="Nächster Halt", value=f"__{next_stop_station}__", inline=False)
    
    route_fields = format_stop_list(stops, next_stop_station)
    for field_name, field_value in route_fields:
        embed.add_field(name=field_name, value=field_value, inline=False)

    footer = build_embed_footer(trip["mode"], metadata["slogans"])
    embed.set_footer(text=footer["text"], icon_url=footer["icon"])

    embed.set_author(name=agency)
    embed.set_thumbnail(url=metadata["logo"])

    return embed

def build_announcement_embed(msg):
    from src.dc.handlers import trip
    agency = trip["agency"]
    metadata = get_operator_metadata(agency, trip["route_color"])

    embed = discord.Embed(
        title = "Informationen zu ihrer Fahrt",
        description=msg,
        color=metadata["color"]
    )

    embed.set_author(name=agency)
    embed.set_thumbnail(url=metadata["logo"])

    footer = build_embed_footer(trip["mode"], metadata.get("slogan"))
    embed.set_footer(text=footer["text"], icon_url=footer["icon"])

    return embed

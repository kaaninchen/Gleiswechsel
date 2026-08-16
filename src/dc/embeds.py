import discord
import random

from src.utils import get_operator_metadata, get_next_station
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
    next_stop = get_next_station(trip["stops"])

    embed = discord.Embed(
        title = trip["long_name"],
        description=f"Abfahrt von {trip["station"]} um {departure}. Ankunft um {arrival}",
        color = metadata["color"]
    )

    stops = trip["stops"]

    if len(stops) > 2:
        count = min(3, len(stops))
        random_stops = random.sample(list(stops), k=count)

        via = ", ".join(random_stops[:-1]) + " und " + random_stops[-1] + ". Nächster Halt: " + next_stop["name"]
        embed.add_field(name="Über", value=via, inline=False)

    field_lines, field_length, part = [], 0, 1

    for name, stop_arrival in stops.items():
        if name == next_stop["name"]:
            line = f"**• {name} ({stop_arrival} Uhr)**"
        else:
            line = f"• {name} ({stop_arrival} Uhr)"

        if field_length + len(line) + 1 > 1024:
            route_page_name = "Route"
            if part != 1:
                route_page_name += " (Fortsetzung)"
            embed.add_field(name=route_page_name, value="\n".join(field_lines), inline=False)
            field_lines, field_length, part = [], 0, part + 1

        field_lines.append(line)
        field_length += len(line) + 1

    if field_lines:
        embed.add_field(name="Route" if part == 1 else "Route (Fortsetzung)", value="\n".join(field_lines), inline=False)

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

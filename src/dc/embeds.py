import discord
import random

from src.utils import convert_iso_string, get_operator_metadata
from src.dc.helpers import format_timestamp_to_dc

def build_embed_footer(mode: str, slogans):
    footer_notice = f"Data provided by https://transitous.org • mode: {mode}"
    icon = "https://avatars.githubusercontent.com/u/24960008?s=60&v=4"

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

    if len(stops) > 2:
        count = min(3, len(stops))
        random_stops = random.sample(list(stops), k=count)

        via = ", ".join(random_stops[:-1]) + " und " + random_stops[-1]
        embed.add_field(name="Über", value=via, inline=False)


    route_lines = []
    for stop_name, stop_arrival in stops.items():
        if stop_name == trip["station"]:
            route_lines.append(f"**• {stop_name} ({stop_arrival} Uhr)**")
        else:
            route_lines.append(f"• {stop_name} ({stop_arrival} Uhr)")
    embed.add_field(name="Route", value="\n".join(route_lines))

    footer = build_embed_footer(trip["mode"], metadata["slogans"])
    embed.set_footer(text=footer["text"], icon_url=footer["icon"])

    embed.set_author(name=agency)
    embed.set_thumbnail(url=metadata["logo"])

    return embed
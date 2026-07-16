import random
import discord
from datetime import datetime
import src.state as state
from src.utils import operator_infos, format_via_list

def format_timestamp(timestr):
    parsed_time = datetime.strptime(timestr, "%H:%M")
    final_datetime = datetime.now().replace(
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=0,
        microsecond=0
    )
    return discord.utils.format_dt(final_datetime, style="t")

def build_info_embed() -> discord.Embed | None:
    if state.name is None:
        return None

    operator = operator_infos(state.train)

    if len(state.via) == 0:
        embed = discord.Embed(
            title=state.name,
            description=f"Abfahrt von {state.station} um {format_timestamp(state.departure)}",
            color=operator["color"]
        )
    else:
        embed = discord.Embed(
            title=state.name,
            description=f"Abfahrt **{format_timestamp(state.departure)}** von **{state.station}**",
            color=operator["color"]
        )
        embed.add_field(name="Über", value=format_via_list(state.via), inline=False)

    embed.set_author(name=operator["name"])
    embed.set_thumbnail(url=operator["logo"])

    route_lines = []
    for stop in state.route:
        stop_name = stop["name"]
        if stop_name == state.station:
            route_lines.append(f"• **{stop_name}**")
        else:
            route_lines.append(f"• {stop_name}")

    embed.add_field(name="Route", value="\n".join(route_lines))

    slogans = operator.get("slogan")
    footer_text = (
        f"{random.choice(slogans)} • Daten großzügig bereitgestellt von dbf.finalrewind.org"
        if slogans else
        "Daten großzügig bereitgestellt von dbf.finalrewind.org"
    )
    embed.set_footer(text=footer_text, icon_url="https://dbf.finalrewind.org/static/icons/icon-96x96.png")

    return embed

def build_error_embed(errormsg) -> discord.Embed:
    embed = discord.Embed(
        title="Ein Fehler ist aufgetreten!",
        description=errormsg,
        color=discord.Colour.red()
    )

    return embed
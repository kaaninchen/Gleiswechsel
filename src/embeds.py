import random
import discord
from datetime import datetime, timedelta
import src.handlers as handlers
from src.utils import operator_metadata, format_via_list, resolve_operator, logger

def format_timestamp(timestr):
    parsed_time = datetime.strptime(timestr, "%H:%M")
    now = datetime.now()
    final_datetime = datetime.now().replace(
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=0,
        microsecond=0
    )

    if final_datetime <= now:
        final_datetime += timedelta(days=1)

    return discord.utils.format_dt(final_datetime, style="t")

def format_iso_timestamp(isostr):
    parsed_time = discord.utils.parse_time(isostr)
    return discord.utils.format_dt(parsed_time, style="t")

def build_info_embed() -> discord.Embed | None:
    conn = handlers.current
    info = handlers.train_info

    if handlers.current is None and handlers.train_info is None:
        return None

    current_operator = resolve_operator(info["operators"])
    arrival = format_iso_timestamp(info["arrival"])
    departure = format_timestamp(conn['departure'])

    operator_infos = operator_metadata(current_operator)

    embed = discord.Embed(
        title=handlers.train_name,
        description=f"Abfahrt von {conn['station']} um {departure}. Ankunft um {arrival}",
        color=operator_infos["color"]
    )

    if len(conn['via']) > 0:
        embed.add_field(name="Über", value=format_via_list(conn['via']), inline=False)

    if operator_infos.get("unknown"): 
        logger(f"WARNING: {current_operator} nicht in operators.py gefunden")
    
    embed.set_author(name=current_operator)
    embed.set_thumbnail(url=operator_infos["logo"])

    route_lines = []
    for stop in conn['route']:
        stop_name = stop["name"]
        if stop_name == conn['station']:
            route_lines.append(f"• **{stop_name}**")
        else:
            route_lines.append(f"• {stop_name}")

    embed.add_field(name="Route", value="\n".join(route_lines))

    slogans = operator_infos.get("slogan")
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
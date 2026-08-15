import discord
import asyncio
from datetime import datetime

from src.api import transitous
from src.utils import logger, channel_formatting

_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot, voice_channel, from_scheduler: bool = False):
    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    station_id = transitous.get_random_stop_id()
    trip_id = transitous.get_random_connection(station_id)
    trip = transitous.get_trip_details(trip_id)

    arrival = datetime.fromisoformat(trip["end_time"])
    long_name = trip["long_name"]

    print("-----------------")
    logger(f"Umstieg: {long_name}, Ankunft: {arrival}")
    logger(f"Betreiber: {trip["agency"]}, Typ: {trip["mode"]}")
    logger(f"Versuche Namen zu ändern, wenn nichts passiert bin ich im cooldown... (warte bis zu 10min!)")

    formatting = channel_formatting(trip["mode"])
    await voice_channel.edit(name=f"{formatting}{long_name}")
    await voice_channel.set_status(f"Ankunft um {arrival.strftime('%H:%M')}")

    logger(f"Name geändert!")


import discord
import asyncio

from src.api import transitous
from src.utils import logger

_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot, voice_channel, from_scheduler: bool = False):
    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    station_id = transitous.get_random_stop_id()
    trip_id = transitous.get_random_connection(station_id)
    trip = transitous.get_trip_details(trip_id)

    train_name = trip["long_name"]
    
    print("-----------------")
    logger(f"Umstieg: {train_name}")
    logger(f"Betreiber: {trip["agency"]}, Typ: {trip["mode"]}")
    logger(f"Sprachkanal wird geändert, wenn nichts passiert bin ich im cooldown (warte einen moment!)")

    await voice_channel.edit(name=train_name)
    logger(f"Name geändert!")


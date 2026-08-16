import discord
import asyncio
from datetime import datetime, timedelta, date

from src.utils import logger, channel_formatting, choose_connection

_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot, voice_channel, from_scheduler: bool = False):
    global trip, _scheduled_task
    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    trip = choose_connection()
    arrival = trip["arrival"]
    long_name = trip["long_name"]

    print("-----------------")
    logger(f"Umstieg: {long_name}, Ankunft: {arrival} Uhr")
    logger(f"Betreiber: {trip["agency"]}, Typ: {trip["mode"]}")
    logger(f"Versuche Namen zu ändern, wenn nichts passiert bin ich im cooldown... (warte bis zu 10min!)")

    formatting = channel_formatting(trip["mode"])
    await voice_channel.edit(name=f"{formatting}{long_name}")
    await voice_channel.set_status(f"Ankunft um {arrival}")

    logger(f"Name geändert!")

    _scheduled_task = asyncio.create_task(_schedule_next_transfer(bot, arrival))

async def _schedule_next_transfer(bot, arrival):
    now = datetime.now()
    parsed_time = datetime.strptime(arrival, "%H:%M").time()
    arrival_dt = datetime.combine(date.today(), parsed_time)

    if arrival_dt < now:
        arrival_dt += timedelta(days=1)

    wait_seconds = (arrival_dt - now).total_seconds()
    if wait_seconds > 0:
        remaining = str(timedelta(seconds=wait_seconds))
        logger(f"Nächster Umstieg in {remaining.split('.')[0]} ({arrival} Uhr)")

        await asyncio.sleep(wait_seconds)

    logger("Zug angekommen, wähle neue Verbindung")
    await rename_vc(bot, from_scheduler=True)


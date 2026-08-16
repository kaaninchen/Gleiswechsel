import discord
import asyncio
from datetime import datetime, timedelta, date

from src.utils import logger, channel_formatting, choose_connection

_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot, voice_channel, from_scheduler: bool = False):
    global trip, _scheduled_task
    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    attempt = 0
    max_attempt = 10
    trip = choose_connection()
    while trip is None and attempt < max_attempt:
        attempt += 1
        logger(f"Attempt {attempt}: Failed to select route, retrying...", "error")
        trip = choose_connection()

    if trip is None:
        logger(f"Failed to select route after {max_attempt} attempts", "fatal")
        return False
    
    arrival = trip["arrival"]
    long_name = trip["long_name"]
    mode = trip["mode"]

    print("-----------------")
    logger(f"Umstieg: {long_name}; Ankunft: {arrival} Uhr")
    logger(f"Betreiber: {trip["agency"]}, Typ: {mode}")
    logger(f"Versuche Namen zu ändern, wenn nichts passiert bin ich im cooldown... (warte bis zu 10min!)")

    formatting = channel_formatting(mode)
    await voice_channel.edit(name=f"{formatting}{long_name}")
    await voice_channel.set_status(f"Ankunft um {arrival}")

    logger(f"Name geändert!")

    _scheduled_task = asyncio.create_task(_schedule_next_transfer(bot, arrival, voice_channel))

async def _schedule_next_transfer(bot, arrival, voice_channel):
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
    await rename_vc(bot, voice_channel, from_scheduler=True)


import discord
import asyncio
import aiohttp
import random
from datetime import datetime, timedelta

from src.utils import logger, channel_formatting, choose_connection, get_sound_path, LOCAL_TZ, get_next_station, generate_static_map
from src.config import config
from src.lang.locales import lang

_scheduled_task: asyncio.Task | None = None
_next_stop_task: asyncio.Task | None = None
channel_lang = lang.channel

async def rename_vc(bot: discord.Bot, voice_channel, from_scheduler: bool = False):
    global trip, _scheduled_task
    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    attempt = 0
    max_attempt = 30
    trip = choose_connection()
    while trip is None and attempt < max_attempt:
        attempt += 1
        trip = choose_connection()

    if trip is None:
        logger(f"Failed to select route after {max_attempt} attempts", "fatal")
        return False

    generate_static_map(trip["stops"], trip["mode"], trip["agency"], trip["route_color"])
    
    arrival = trip["arrival"]
    channel_name = trip["channel_name"]

    mode = trip["mode"]

    print("-----------------")
    logger(f"Transfer: {channel_name}; Arrival: {arrival}")
    logger(f"Agency: {trip["agency"]}, mode: {mode}")
    logger(f"Trying to change the channels name. If nothing happens, then the bot is in cooldown... (automatically resolves after up to 10min)")

    formatting = channel_formatting(mode)
    await voice_channel.edit(name=f"{formatting}{channel_name}")
    await voice_channel.set_status(None)
    start_next_stop_updates(voice_channel)

    logger(f"Updated channel name!")

    await bot.change_presence(activity=discord.Game(name=lang.rich_presence.arrival()))
    await announcer("transfer", voice_channel)

    _scheduled_task = asyncio.create_task(_schedule_next_transfer(bot,  trip["arrival_dt"], voice_channel, trip["to"]))

async def announcer(announcement: str, voice_channel: discord.VoiceChannel, destination = None):
    from src.dc.embeds import build_info_embed, build_announcement_embed
    announcements_enabled = config.announcements.text_announcements

    if announcements_enabled:
        image = None
        if len(voice_channel.members) > 0:
            match announcement:
                case "end_of_connection":
                        embed = build_announcement_embed(lang.embeds.announcement.end_of_connection.message())
                case "transfer":
                    embed = build_info_embed()
                    image = discord.File("src/data/assets/current_map.png", filename="ride.png")
                case _:
                    logger(f"Unknown announcement: {announcement}")
                    embed = None

            if embed:
                if image:
                    await voice_channel.send(file=image, embed=embed)
                else:
                    await  voice_channel.send(embed=embed)

async def voice_announcer(station: str, voice_channel: discord.VoiceChannel) -> bool:
    sound_path = get_sound_path(station=station)
    if sound_path is None:
        return False

    if voice_channel.guild.voice_client:
        logger(f"Already in vc, skipping this announcement to be safe")
        return False
    
    logger(f"Joining vc, playing {sound_path}")

    connect_task = asyncio.create_task(voice_channel.connect(timeout=15, reconnect=True))
    audio_source = discord.FFmpegPCMAudio(sound_path)

    vc = await connect_task

    loop = asyncio.get_running_loop()

    if not vc.is_playing():
        def after_playing(error):
            if error:
                logger(f"Player error: {error}", "error")
            loop.create_task(vc.disconnect())
            logger("Leaving vc")

        vc.play(audio_source, after=after_playing)
        return True

async def _schedule_next_transfer(bot: discord.Bot, arrival_dt: datetime, voice_channel: discord.VoiceChannel, destination: str):
    now = datetime.now(LOCAL_TZ)

    wait_seconds = (arrival_dt - now).total_seconds()
    announcement_countdown = random.randrange(180, 300)

    if wait_seconds > 0:
        remaining = str(timedelta(seconds=wait_seconds))
        logger(f"Next transfer in {remaining.split('.')[0]} ({arrival_dt.strftime('%H:%M')})")

        if wait_seconds > announcement_countdown:
            wait_until_end_announcement = wait_seconds - announcement_countdown
            await asyncio.sleep(wait_until_end_announcement)
            await announcer("end_of_connection", voice_channel, destination)
            await asyncio.sleep(announcement_countdown)
        else:
            await asyncio.sleep(wait_seconds)

        logger("Train arrived, searching for a new connection....")
        await rename_vc(bot, voice_channel, from_scheduler=True)

async def _update_next_loop(voice_channel: discord.VoiceChannel):
    global trip
    try:
        if trip is None:
            return

        now = datetime.now(LOCAL_TZ)
        departure_dt = trip["departure_dt"]

        if departure_dt > now:
                wait_seconds = (departure_dt - now).total_seconds() + 10
                await asyncio.sleep(wait_seconds)

        while True:
            next_stop = get_next_station(trip["stops"], trip["from"])

            if next_stop is None:
                return
            
            next_stop_str = next_stop["name"]
            
            status_text = f"{lang.embeds.info.next_stop()}: {next_stop_str}"
            
            try:
                await voice_channel.set_status(status_text, reason="Next stop status")
            except aiohttp.ClientConnectorDNSError as e:
                logger(F"Failed to set the channel status (network error?): {e}", "error")

            if config.announcements.voice_announcements:
                if len(voice_channel.members) > 0:
                    await voice_announcer(next_stop_str, voice_channel)

            wait_seconds = (next_stop["arrival"] - datetime.now(LOCAL_TZ)).total_seconds()
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)

    except asyncio.CancelledError:
        raise

def start_next_stop_updates(voice_channel: discord.VoiceChannel):
    global _next_stop_task

    if _next_stop_task is not None and not _next_stop_task.done():
        _next_stop_task.cancel()

    _next_stop_task = asyncio.create_task(_update_next_loop(voice_channel))
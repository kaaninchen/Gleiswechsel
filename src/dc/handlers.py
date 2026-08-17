import discord
import asyncio
import random
from datetime import datetime, timedelta, date

from src.utils import logger, channel_formatting, choose_connection, get_sound_path, LOCAL_TZ
from src.config import config

_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot, voice_channel, from_scheduler: bool = False):
    global trip, _scheduled_task
    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    attempt = 0
    max_attempt = 15
    trip = choose_connection()
    while trip is None and attempt < max_attempt:
        attempt += 1
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

    await announcer("umstieg", voice_channel)

    _scheduled_task = asyncio.create_task(_schedule_next_transfer(bot,  trip["arrival_dt"], voice_channel, trip["to"]))

            
async def _schedule_next_transfer(bot: discord.Bot, arrival_dt: datetime, voice_channel: discord.VoiceChannel, destination: str):
    now = datetime.now(LOCAL_TZ)

    wait_seconds = (arrival_dt - now).total_seconds()
    announcement_countdown = random.randrange(180, 300)

    if wait_seconds > 0:
        remaining = str(timedelta(seconds=wait_seconds))
        logger(f"Nächster Umstieg in {remaining.split('.')[0]} ({arrival_dt.strftime('%H:%M')} Uhr)")

        if wait_seconds > announcement_countdown:
            wait_until_end_announcement = wait_seconds - announcement_countdown
            await asyncio.sleep(wait_until_end_announcement)
            await announcer("ende", voice_channel, destination)
            await asyncio.sleep(announcement_countdown)
        else:
            await asyncio.sleep(wait_seconds)

    logger("Zug angekommen, wähle neue Verbindung")
    await rename_vc(bot, voice_channel, from_scheduler=True)

async def announcer(announcement: str, voice_channel: discord.VoiceChannel, destination = None):
    from src.dc.embeds import build_info_embed, build_announcement_embed
    announcements_enabled = config.announcements.enabled
    voice_announcement_enabled = config.announcements.voice[0].enabled

    if announcements_enabled:
        if len(voice_channel.members) > 0:
            match announcement:
                case "ende":
                    embed = build_announcement_embed(
                        f'Sehr geehrte Fahrgäste,\nIn wenigen Minuten erreichen wir {destination}. Dieser Zug endet dort.\n\nWir wünschen Ihnen eine angenehme Weiterreise.\n\nVielen Dank für ihr Vertrauen und auf Wiedersehen.')
                    if voice_announcement_enabled:
                        await voice_announcer(destination, voice_channel)
                case "umstieg":
                    embed = build_info_embed()
                case _:
                    logger(f"Unbekanntes Announcements: {announcement}")
                    embed = None
            if embed:
                await voice_channel.send(embed=embed)
        else:
            logger(f"Announcement {announcement} wird geskipped, keiner da")
            return

async def voice_announcer(destination: str, voice_channel: discord.VoiceChannel):
    sound_path = get_sound_path(destination=destination)
    if sound_path is None:
        return
    
    logger(f"VC wird betreten, spiele {sound_path}")
    vc = await voice_channel.connect(timeout=15, reconnect=True)
    audio_source = discord.FFmpegPCMAudio(sound_path)

    loop = asyncio.get_running_loop()

    if not vc.is_playing():
        def after_playing(error):
            if error:
                logger(f"Player error: {error}", "error")
            loop.create_task(vc.disconnect())
            logger("VC wird verlassen")

        vc.play(audio_source, after=after_playing)
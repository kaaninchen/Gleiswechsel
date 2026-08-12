import discord
from datetime import datetime, timedelta
import asyncio
import random
from pathlib import Path

from src.config import config
from src.utils import random_connection, get_train_info, get_channel_formatting, logger
from src.embeds import build_announcement_embed, build_info_embed

current = None
_scheduled_task: asyncio.Task | None = None

async def announcer(bot, announcement):
    voice_channel = bot.get_channel(config["vc"])
    if len(voice_channel.members) > 0:
        match announcement:
            case "ende":
                destination = current['destination']
                embed = build_announcement_embed(
                    f'Sehr geehrte Fahrgäste,\nIn wenigen Minuten erreichen wir {destination}. Dieser Zug endet dort.\n\nWir wünschen Ihnen eine angenehme Weiterreise.\n\nVielen Dank für Ihr Vertrauen und auf Wiedersehen.')
                if config["voice_announcements"][0]["enabled"]:
                    await voice_announcer(bot, destination, voice_channel)
            case "umstieg":
                embed = build_info_embed()
            case _:
                embed = None
        if embed is None:
            logger(f"Unbekanntes Announcement: {announcement}")
        else:
            await voice_channel.send(embed=embed)
    else:
        logger(f"Announcement {announcement} wird geskipped, keiner da")
        return

async def voice_announcer(bot: discord.Bot, destination, voice_channel):
    voice_announcement_config = config["voice_announcements"][0]
    voice_stations = voice_announcement_config["stations"]

    if destination in voice_stations:
        announcement_for = destination
    else:
        if voice_stations.get("general", "") == "":
            return
        announcement_for = "general"

    if voice_stations.values() == list:
        sound_file = random.choice(voice_stations.get(announcement_for))
    else:
        sound_file = voice_stations.get(announcement_for)

    sound_path = f"src/data/announcements/{sound_file}"
    if Path(sound_path).is_file() is False:
        logger(f"Konnte Datei {sound_path} nicht finden", "error")
        return

    logger(f"VC wird betreten, spiele {sound_path}")
    vc = await voice_channel.connect(timeout=15, reconnect=True)
    audio_source = discord.FFmpegPCMAudio(sound_path)

    if not vc.is_playing():
        def after_playing(error):
            if error:
                logger(f"Player error: {error}", "error")
            bot.loop.create_task(vc.disconnect())
            logger("VC wird verlassen")

        vc.play(audio_source, after=after_playing)

async def rename_vc(bot: discord.Bot, from_scheduler: bool = False):
    global current, train_name, train_info, train_type, _scheduled_task

    guild = bot.get_guild(int(config["server"]))
    if guild is None:
        logger(f"Es konnte kein Server mit der ID {config['server']} gefunden werden! Ist der Bot ein Member?", "fatal")
        return False

    channel = guild.get_channel(int(config["vc"]))
    if not isinstance(channel, discord.VoiceChannel):
        logger(f"Es konnte kein VC mit der ID {config['vc']} auf dem Server gefunden werden", "fatal")
        return False

    if not from_scheduler and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    attempt = 0
    while True:
        if attempt == 20:
            logger("Zu viele Fehlversuche. Füge einen anderen Bahnhof hinzu.", "fatal")
            return "Es konnte kein Zug gefunden werden."
        
        attempt += 1
        current = random_connection()
        if current == None:
            return None

        parts = current['train'].split()
        train_type = parts[0]

        if parts[1].isdigit():
            train = current['train']
            train_ID = parts[1]
        else:
            train = parts[1]
            train_ID = current['train_number']

        station = current['station']
        train_info = get_train_info(station=station, train_ID=train_ID, train_type=train_type)
        if train_info and train_info.get('operators') and train_info.get('arrival'):
            break

        logger(f"Versuch {attempt}: Fehler bei {current['train']} von {station}, versuche neue Verbindung...")

    train_name = f"{train} nach {current['destination']} von {current['station']}"
    logger(f"Vorbereitung auf {train_name} (typ: {train_type})")
    arrival = datetime.fromisoformat((train_info["arrival"]))
    formatting = get_channel_formatting(train_type)


    print("-----------------------------------------")
    logger(f"Umstieg: {train_name}")
    logger(f"Betreiber: {''.join(train_info['operators'])}")
    logger(f"Train-Type: {train_type}")
    logger(f"Wenn der Name nicht geändert wird bin ich im Cooldown")
    await channel.edit(name=f"{formatting}{train_name}")
    await channel.set_status(f"Ankunft um {arrival.strftime('%H:%M')}")
    logger(f"Name geändert!")

    if config.get("announcements", True):
        await announcer(bot, "umstieg")

    _scheduled_task = asyncio.create_task(_schedule_next_umstieg(bot, arrival))

    return True

async def _schedule_next_umstieg(bot, arrival):
    announcement = config.get("announcements", True)
    announcement_countdown = random.randrange(180, 300)  # letzte station announcement ist meistens 3-5min vor ankunft
    wait_seconds = (arrival - datetime.now()).total_seconds()
    if wait_seconds > 0:
        remaining = str(timedelta(seconds=wait_seconds))
        logger(f"Nächster Umstieg in {remaining.split('.')[0]} ({arrival.strftime('%H:%M:%S')} Uhr)")
        
        if announcement and wait_seconds > announcement_countdown:
            wait_until_end_announcement = wait_seconds - announcement_countdown
            await asyncio.sleep(wait_until_end_announcement)
            await announcer(bot, "ende")
            await asyncio.sleep(announcement_countdown)

        else:
            await asyncio.sleep(wait_seconds)

    logger("Zug angekommen, wähle neue Verbindung...")
    await rename_vc(bot, from_scheduler=True)
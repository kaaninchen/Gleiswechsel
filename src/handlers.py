import discord
from datetime import datetime, timedelta
import asyncio
from src.config import config
from src.utils import random_connection, get_train_info, logger

current = None
_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot):
    global current, train_name, train_info, _scheduled_task

    guild = bot.get_guild(int(config["server"]))
    if guild is None:
        logger(f"Es konnte kein Server mit der ID {config['server']} gefunden werden! Ist der Bot ein Member?")
        return False

    channel = guild.get_channel(int(config["vc"]))
    if not isinstance(channel, discord.VoiceChannel):
        logger(f"Es konnte kein VC mit der ID {config['vc']} auf dem Server gefunden werden")
        return False

    attempt = 0
    while True:
        if attempt == 3:
            logger("Zu viele Fehlversuche. Füge einen anderen Bahnhof hinzu.")
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

    _scheduled_task = asyncio.create_task(_schedule_next_umstieg(bot, arrival))

    print("-----------------------------------------")
    logger(f"Umstieg: {train_name}")
    logger(f"Betreiber: {train_info['operators']}")
    logger(f"Wenn der Name nicht geändert wird bin ich im Cooldown")
    await channel.edit(name=f"{config['formatting']}{train_name}")
    await channel.set_status(f"Ankunft um {arrival.strftime('%H:%M')}")
    logger(f"Name geändert!")

    return True

async def _schedule_next_umstieg(bot, arrival):
    wait_seconds = (arrival - datetime.now()).total_seconds()
    if wait_seconds > 0:
        remaining = str(timedelta(seconds=wait_seconds))
        logger(f"Nächster Umstieg in {remaining.split(".")[0]} ({arrival.strftime('%H:%M:%S')} Uhr)")
        await asyncio.sleep(wait_seconds)
    logger("Zug angekommen, wähle neue Verbindung...")
    await rename_vc(bot)
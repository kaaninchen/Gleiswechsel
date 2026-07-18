import discord
from datetime import datetime, timedelta
import asyncio
from src.config import config
from src.utils import random_connection, get_train_info, logger

current = None
_scheduled_task: asyncio.Task | None = None

async def rename_vc(bot: discord.Bot, scheduled=False) -> bool:
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
        if attempt > 3:
            logger("Zu viele Fehlversuche. Füge einen anderen Bahnhof hinzu.")
            return "Es konnte kein Zug gefunden werden."
        
        attempt += 1
        current = random_connection()
        train_type = current['train'].split()[0]

        if train_type in ("IC", "ICE", "NJ", "ES", "DZ", "RJ"):
            train = current['train']
            train_ID = current['train'].split()[1]
        else:
            train = current['train'].split()[1]
            train_ID = current['train_number']

        train_info = get_train_info(station=current['station'], train_ID=train_ID, train_type=train_type)

        if train_info:
            break

        logger(f"Versuch {attempt}: Keine Ankunftszeit für {current['train']} verfügbar, versuche neue Verbindung...")

    train_name = f"{train} nach {current['destination']}"

    if not scheduled and _scheduled_task and not _scheduled_task.done():
        _scheduled_task.cancel()

    _scheduled_task = asyncio.create_task(_schedule_next_umstieg(bot, train_info["arrival"]))

    print("-----------------------------------------")
    logger(f"Umstieg: {train_name} von {current['station']}")
    logger(f"Betreiber: {train_info['operators']}")
    logger(f"Wenn der Name nicht geändert wird bin ich im Cooldown")
    await channel.edit(name=f"{config['formatting']}{train_name}")
    logger(f"Name geändert!")

    return True

async def _schedule_next_umstieg(bot, arrival_iso):
    try:
        arrival = datetime.fromisoformat(arrival_iso)
        wait_seconds = (arrival - datetime.now()).total_seconds()

        
        if wait_seconds > 0:
            remaining = str(timedelta(seconds=wait_seconds))
            logger(f"Um {arrival.strftime('%H:%M:%S')} gehts weiter (in {remaining.split("."[0])})!...")
            await asyncio.sleep(wait_seconds)
        logger("Zug angekommen, wähle neue Verbindung...")
        await rename_vc(bot, scheduled=True)
    
    except asyncio.CancelledError:
        logger("Geplanter Umstieg wurde abgebrochen (manueller /umstieg dazwischen oder CTRL + C)")
        raise
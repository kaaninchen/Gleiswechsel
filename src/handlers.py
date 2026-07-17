import discord
import time
from src.config import config
from src.utils import random_connection

current = None

async def rename_vc(bot: discord.Bot) -> bool:
    global current, train_name

    guild = bot.get_guild(int(config["server"]))
    if guild is None:
        print(f"Es konnte kein Server mit der ID {config['server']} gefunden werden! Ist der Bot ein Member?")
        return False

    channel = guild.get_channel(int(config["vc"]))
    if not isinstance(channel, discord.VoiceChannel):
        print(f"Es konnte kein VC mit der ID {config['vc']} auf dem Server gefunden werden")
        return False
    
    current = random_connection()
    train_type = current['train'].split()[0]
    if train_type in ("IC", "ICE", "NJ"):
        train = current['train']
    else:
        train = current['train'].split()[1]
    train_name = f"{train} nach {current['destination']}"

    print("-----------------------------------------")
    current_time = time.strftime('%X')
    print(f"{current_time}: Umstieg: {train_name} (Typ {train_type}) von {current['station']}")
    print(f"{current_time}: Wenn hier keine Nachricht mehr kommt bin ich im Cooldown")
    await channel.edit(name=f"{config['formatting']}{train_name}",)
    print(f"{current_time}: Name geändert!")
    return True
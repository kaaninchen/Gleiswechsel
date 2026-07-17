import discord
from config import config
from src.utils import random_connection

current = None

async def rename_vc(bot: discord.Bot) -> bool:
    global current, name

    guild = bot.get_guild(int(config["server"]))
    if guild is None:
        print(f"Guild {config['server']} not found! Is the bot a member?")
        return False

    channel = guild.get_channel(int(config["vc"]))
    if not isinstance(channel, discord.VoiceChannel):
        print(f"Unable to find voice-Channel {config['vc']} on the server")
        return False
    
    current = random_connection()
    name = f"{current['train']} nach {current['destination']}"

    print(f"Info: {name} from {current['station']} \n via: {current['via']}")

    await channel.edit(name=f"{config['formatting']}{name}",)
    return True
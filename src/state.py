import discord
from config import config
from src.utils import random_connection

name = None
train = None
route = None
departure = None
via = None
station = None

async def rename_vc(bot: discord.Bot) -> bool:
    global name, train, route, departure, via, station

    guild = bot.get_guild(int(config["server"]))
    if guild is None:
        print(f"Guild {config['server']} not found! Is the bot a member?")
        return False

    channel = guild.get_channel(int(config["vc"]))
    if not isinstance(channel, discord.VoiceChannel):
        print(f"Unable to find voice-Channel {config['vc']} on the server")
        return False
    
    train, destination, route, departure, via, station = random_connection()
    name = f"{train} nach {destination}"

    print(f"Info: {name} from {station}\n via: {via}")

    await channel.edit(name=f"{config['formatting']}{name}")
    return True
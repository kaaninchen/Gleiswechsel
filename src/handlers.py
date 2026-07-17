import discord
from config import config
from src.utils import random_connection

current = None

async def rename_vc(bot: discord.Bot) -> bool:
    global current, train_name

    guild = bot.get_guild(int(config["server"]))
    if guild is None:
        print(f"Guild {config['server']} not found! Is the bot a member?")
        return False

    channel = guild.get_channel(int(config["vc"]))
    if not isinstance(channel, discord.VoiceChannel):
        print(f"Unable to find voice-Channel {config['vc']} on the server")
        return False
    
    current = random_connection()

    if current['train'].split()[0] == "IC" or current['train'].split()[0] == "ICE":
        train = current['train']
    else:
        train = current['train'].split()[1]
    train_name = f"{train} nach {current['destination']}"

    print(f"Info: {train_name} from {current['station']} \n via: {current['via']}")

    await channel.edit(name=f"{config['formatting']}{train_name}",)
    return True
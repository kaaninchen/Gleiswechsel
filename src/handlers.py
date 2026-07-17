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
    train_type = current['train'].split()[0]
    if train_type in ("IC", "ICE", "NJ"):
        train = current['train']
    else:
        train = current['train'].split()[1]
    train_name = f"{train} nach {current['destination']}"

    print(f"Umstieg: {train_name} von {current['station']} \nüber: {current['via']}")
    await channel.edit(name=f"{config['formatting']}{train_name}",)
    return True
import discord
from  src.utils import logger

def validate_channel(bot: discord.bot, server_id: int, channel_id: int):
    guild = bot.get_guild(server_id)
    channel = guild.get_channel(channel_id)

    if guild is None:
        logger(f"Es konnte kein Server mit der ID {server_id} gefunden werden", "fatal")

    if not isinstance(channel, discord.VoiceChannel):
        logger(f"Es konnte kein VC mit der id {channel_id} gefunden werden", "fatal")
        return False

    return channel
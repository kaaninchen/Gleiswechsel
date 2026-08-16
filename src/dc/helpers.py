import discord
from datetime import datetime, timedelta
from  src.utils import logger

def validate_channel(bot: discord.bot, server_id: int, channel_id: int):
    guild = bot.get_guild(server_id)

    if guild is None:
        logger(f"Es konnte kein Server mit der ID {server_id} gefunden werden", "fatal")
        return False

    channel = guild.get_channel(channel_id)
    if not isinstance(channel, discord.VoiceChannel):
        logger(f"Es konnte kein VC mit der id {channel_id} gefunden werden", "fatal")
        return False

    return channel

def format_timestamp_to_dc(timestr):
    parsed_time = datetime.strptime(timestr, "%H:%M")
    now = datetime.now()
    final_datetime = datetime.now().replace(
        hour=parsed_time.hour,
        minute=parsed_time.minute,
        second=0,
        microsecond=0
    )

    if final_datetime <= now:
        final_datetime += timedelta(days=1)

    return discord.utils.format_dt(final_datetime, style="t")
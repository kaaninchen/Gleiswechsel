import discord
from src.utils import config, logger
from src.dc.handlers import rename_vc
from src.dc.helpers import validate_channel

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    server_id = config["server"]
    server_vc_id = config["vc"]
    channel = validate_channel(bot=bot, server_id=server_id, channel_id=server_vc_id)

    logger(f"{bot.user} ist online")
    await rename_vc(bot=bot, voice_channel=channel)

try:
    bot.run(config["token"])
except:
    logger("Feher peim parsen des tokens", "fatal")
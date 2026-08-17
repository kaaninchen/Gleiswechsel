import discord
import sys

from src.utils import logger
from src.config import config
from src.dc.handlers import rename_vc
from src.dc.helpers import validate_channel
from src.dc.commands import setup_commands
from src.api.transitous import check_stations

bot = discord.Bot(intents=discord.Intents.all())
setup_commands(bot=bot)
_bot_initialized = False

if len(sys.argv) > 1:
    if sys.argv[1] == "stations":
        check_stations()
        sys.exit(0)

@bot.event
async def on_ready():
    global _bot_initialized

    if not _bot_initialized:
        logger(f"{bot.user} ist online")
        _bot_initialized = True
        server_id = config.discord.server
        server_vc_id = config.discord.vc
        channel = validate_channel(bot=bot, server_id=server_id, channel_id=server_vc_id)
        await rename_vc(bot, voice_channel=channel)

try:
    bot.run(config.discord.token)
except:
    logger("Feher peim parsen des tokens", "fatal")

'''
TODO
- discord status
- multi language support
- README
'''
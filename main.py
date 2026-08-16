import discord
from src.utils import config, logger
from src.dc.handlers import rename_vc
from src.dc.helpers import validate_channel
from src.dc.commands import setup_commands

bot = discord.Bot(intents=discord.Intents.all())
setup_commands(bot=bot)
_bot_initialized = False

@bot.event
async def on_ready():
    global _bot_initialized

    logger(f"{bot.user} ist online")

    if not _bot_initialized:
        _bot_initialized = True
        server_id = config["server"]
        server_vc_id = config["vc"]
        channel = validate_channel(bot=bot, server_id=server_id, channel_id=server_vc_id)
        await rename_vc(bot, voice_channel=channel)
    else:
        logger("Reconnected to discord gateway, this wont disturb your current ride")

try:
    bot.run(config["token"])
except:
    logger("Feher peim parsen des tokens", "fatal")

'''
TODO
- 1024 embed limit
- discord status
- text announcements
- voice announcements
- multi language support
- README
'''
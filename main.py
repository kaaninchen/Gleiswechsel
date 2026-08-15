import discord
from src.utils import config, logger
from src.dc.handlers import rename_vc
from src.dc.helpers import validate_channel
from src.dc.commands import setup_commands

bot = discord.Bot(intents=discord.Intents.all())
setup_commands(bot=bot)

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

'''
TODO
- Only choose connections in the future
- discord reconnection handling
- Automatic transfer
- discord status
- text announcements
- voice announcements
- improved error handling (retry connection)
- Footer Notice Slogangs
'''
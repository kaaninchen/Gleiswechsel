import discord
import random
from discord.ext import tasks
from src.config import config
from src.handlers import rename_vc
from src.commands import setup_commands
from src.embeds import build_error_embed
from src.data.status import discord_status

bot = discord.Bot(intents=discord.Intents.all())
setup_commands(bot)

@tasks.loop(minutes=5)
async def change_status():
    status = random.choice(discord_status)
    await bot.change_presence(activity=discord.Game(name=f"{status} • /info"))

@bot.event
async def on_ready():
    print(f"{bot.user} ist online")
    if not change_status.is_running():
        change_status.start()
    await rename_vc(bot)
'''
@bot.event
async def on_application_command_error(ctx, error):
    embed = build_error_embed(f"Ein Fehler ist aufgetreten: {error}")
    await ctx.respond(embed=embed)
'''
try: 
    bot.run(config['token'])
except:
    print("Fehler beim parsen des token", "fatal")
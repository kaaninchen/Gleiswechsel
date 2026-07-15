import discord
from config import config

bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name = "Casino"))
    print(f"{bot.user} ist online")

try: 
    bot.run(config['token'])
except:
    print("An error occured while parsing the token (check the config!)")
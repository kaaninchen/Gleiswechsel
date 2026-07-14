import requests
import json
import random
import discord

with open("config.json", "r") as file:
    config = json.load(file)

bot = discord.Bot(intents=discord.Intents.all())

def random_connection():
    while True:
        station = random.choice(config["stations"])
        url = f"https://dbf.finalrewind.org/{station}.json"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException:
            continue

        departures = [
            d for d in data.get("departures", [])
            if d.get("scheduledDeparture") and d.get("destination") != station
        ]

        if not departures:
            continue

        dep = random.choice(departures)
        return [f"{config["formatting"]}{dep['train']} nach {dep['destination']}", f"von {station}"]

@bot.slash_command(description="Rename vc")
async def rename_vc(ctx):
    channel = bot.get_channel(int(config["vc"]))
    if isinstance(channel, discord.VoiceChannel):
        name, status = random_connection()
        await channel.edit(name = name)
        await channel.set_status(status)
        await ctx.respond("Kanal aktualisiert!")

try: 
    bot.run(config['token'])
except:
    print("An error occured while parsing the token (check the config!)")
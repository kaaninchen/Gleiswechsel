import discord
from discord.ext import commands
from src.embeds import build_info_embed, build_error_embed

def setup_commands(bot: discord.Bot):
    @bot.slash_command(description="Informationen über die aktuelle Fahrt")
    async def info(ctx):
        embed = build_info_embed()
        if embed is None:
            await build_error_embed("Noch keine Verbindung gesetzt.")
            return
        await ctx.respond(embed=embed)

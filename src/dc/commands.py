import discord
from src.dc.embeds import build_info_embed

def setup_commands(bot: discord.Bot):
    @bot.slash_command(description="Informationen über die aktuelle Fahrt")
    async def info(ctx):
        await ctx.respond(embed=build_info_embed())
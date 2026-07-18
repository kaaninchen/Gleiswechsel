import discord
from discord.ext import commands
from src.handlers import rename_vc
from src.embeds import build_info_embed, build_error_embed

def setup_commands(bot: discord.Bot):
    @bot.slash_command(description="Steige in den nächsten Zug! Beachte das Discord Spam limit (2x in 10min)")
    @commands.cooldown(1, 600, commands.BucketType.guild)
    async def umstieg(ctx):
        await ctx.defer()
        rename = await rename_vc(bot)
        if not rename:
            build_error_embed(rename)
        else:
            embed = build_info_embed()
        await ctx.respond("Informationen zur neuen Fahrt:", embed=embed)

    @bot.slash_command(description="Informationen über die aktuelle Fahrt")
    async def info(ctx):
        embed = build_info_embed()
        if embed is None:
            await ctx.respond("Noch keine Verbindung gesetzt.")
            return
        await ctx.respond(embed=embed)

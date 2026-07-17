import discord
from src.handlers import rename_vc
from src.embeds import build_info_embed, build_error_embed

def setup_commands(bot: discord.Bot):
    @bot.slash_command(description="Steige in den nächsten Zug! Beachte das Discord Spam limit (2x in 10min)")
    async def umstieg(ctx):
        success = await rename_vc(bot)
        if not success:
            await ctx.respond("Kanal nicht gefunden")
            return
        
        embed = build_info_embed()
        await ctx.respond("Informationen zur neuen Fahrt:", embed=embed)

    @bot.slash_command(description="Informationen über die aktuelle Fahrt")
    async def info(ctx):
        embed = build_info_embed()
        if embed is None:
            await ctx.respond("Noch keine Verbindung gesetzt.")
            return
        await ctx.respond(embed=embed)

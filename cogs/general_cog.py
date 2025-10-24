from disnake.ext import commands
from modules.check_roles import has_any_role_by_keys


class GeneralCog(commands.Cog, name="General"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @has_any_role_by_keys("head_administration_role")
    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.bot.latency * 1000)}ms")

from disnake.ext import commands


class EventCog(commands.Cog, name="Event"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} подключен! | {len(self.bot.guilds)} серверов | {len(self.bot.users)} пользователей")

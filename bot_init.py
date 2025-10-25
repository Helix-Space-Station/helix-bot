import importlib
import os

from disnake import Intents
from disnake.ext import commands
from disnake.ext.commands import Bot

from config import Config
from modules.database_manager import DatabaseManagerSS14

# Инициализация бота
intents = Intents.all()
bot = Bot(command_prefix="$", intents=intents, help_command=None)
cfg = Config()


# Инициализация менеджера БД
ss14_db = DatabaseManagerSS14()
# Конфиг основной БД
main_db_config = {
    'database': cfg.DB_DATABASE_SS14_MAIN,
    'user': cfg.DB_USER_SS14_MAIN,
    'password': cfg.DB_PASSWORD_SS14_MAIN,
    'host': cfg.DB_HOST_SS14_MAIN,
    'port': cfg.DB_PORT_SS14_MAIN
}
ss14_db.add_database(
    name='main',
    db_config=main_db_config,
)
ss14_db.add_time_zone(cfg.MOSCOW_TIMEZONE)


async def load_cogs():
    """
    Автоматически загружает все Cog'и из папки cogs/
    """
    cogs_dir = "cogs"
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = f"{cogs_dir}.{filename[:-3]}"
            try:
                module = importlib.import_module(module_name)
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (
                        isinstance(attr, type) and
                        issubclass(attr, commands.Cog)
                    ):
                        bot.add_cog(attr(bot))
                        print(f"Загружен Cog: {attr.__name__}")
            except ImportError as e:
                print(f"Ошибка при импорте {module_name}: {e}")
            except Exception as e:
                print(f"Ошибка при загрузке Cog'а из {module_name}: {e}")


async def start_bot():
    await load_cogs()
    await bot.start(cfg.DISCORD_BOT_TOKEN)


async def stop_bot():
    await bot.close()
    print("Бот остановлен.")

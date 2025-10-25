import os

import dotenv
import pytz

dotenv.load_dotenv()

def get_env_variable(name: str, default: str = "NULL") -> str:
    """
    Функция для безопасного получения переменных окружения.
    Если переменная не найдена, возвращает значение по умолчанию.
    """
    value = os.getenv(name)
    if not value:
        print(f"Предупреждение: {name} не найден в файле .env. "
              f"Используется значение по умолчанию: {default}"
        )
        return default
    return value

class Config:
    """Класс для хранения конфигурационных переменных."""
    # GENERAL
    GUILD_ID = 1429449485536202795
    MY_USER_ID = 328502766622474240
    LOG_CHANNEL_ID = 1429449486157090888
    
    # SS14 AUTH FROM DISCORD
    CHANNEL_AUTH_DISCORD_SS14_ID = 1429449486157090888
    AUTH_MESSAGE_ID = 1352243068220342362
    LOG_TECH_CHANNEL_AUTH_ID = 1429449486157090888

    # MOSCOW TIMEZONE
    MOSCOW_TIMEZONE = pytz.timezone("Europe/Moscow")

    # DATABASE POSTGRESQL
    DISCORD_BOT_TOKEN = get_env_variable("DISCORD_BOT_TOKEN")
    DB_DATABASE_SS14_MAIN = get_env_variable("DB_DATABASE_SS14_MAIN")
    DB_USER_SS14_MAIN = get_env_variable("DB_USER_SS14_MAIN")
    DB_PASSWORD_SS14_MAIN = get_env_variable("DB_PASSWORD_SS14_MAIN")
    DB_HOST_SS14_MAIN = get_env_variable("DB_HOST_SS14_MAIN")
    DB_PORT_SS14_MAIN = get_env_variable("DB_PORT_SS14_MAIN", default="5432")

    # ROLE WHITELIST
    ROLE_WHITELISTS = {
        "head_administration_role": [
            1431407679670059162
            ],
        "general_adminisration_role": [1429449485931848704],
    }

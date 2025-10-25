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
    GUILD_ID = 1429449485536202795
    MY_USER_ID = 328502766622474240
    LOG_CHANNEL_ID = 1429449486157090888
    
    MOSCOW_TIMEZONE = pytz.timezone("Europe/Moscow")

    DISCORD_BOT_TOKEN = get_env_variable("DISCORD_BOT_TOKEN")
    
    ROLE_WHITELISTS = {
        "head_administration_role": [
            1431407679670059162
            ],
        "general_adminisration_role": [1429449485931848704],
    }

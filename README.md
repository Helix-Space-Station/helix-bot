# Helix Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/disnake-Library-5865F2?logo=discord&logoColor=white">
  <img src="https://img.shields.io/badge/python--dotenv-Environment-orange">
  <img src="https://img.shields.io/badge/requests-HTTP%20Client-005571">
  <img src="https://img.shields.io/badge/SS14-Integration-yellowgreen">
  <img src="https://img.shields.io/badge/psycopg2-PostgreSQL-336791">
</p>

<p align="center">
  <img src="https://img.shields.io/github/license/Helix-Space-Station/helix-bot">
  <img src="https://img.shields.io/github/last-commit/Helix-Space-Station/helix-bot">
  <img src="https://img.shields.io/github/languages/top/Helix-Space-Station/helix-bot">
</p>

### 👤 Автор: [Schrödinger](https://github.com/Schrodinger71)

**Helix Bot** — это Discord-бот, созданный с использованием библиотеки `disnake`, предназначенный для интеграции с сервером SS14 (Space Station 14). Бот предоставляет функции привязки аккаунтов SS14 к Discord, модерации, а также другие полезные команды и автоматизированные задачи.


## 📦 Требования

- Python 3.11 или выше
- Библиотека `disnake`
- Библиотека `python-dotenv` (для переменных окружения)
- База данных SS14 (для проверки UID и имён пользователей)


## 🛠️ Установка

1. **Клонируйте репозиторий**:

    ```bash
    git clone https://github.com/Helix-Space-Station/helix-bot
    cd helix-bot
    ```

2. **Создайте виртуальное окружение**:

    ```bash
    python -m venv venv
    ```

3. **Активируйте виртуальное окружение**:

    - **Windows**:
      ```bash
      venv\Scripts\activate
      ```
    - **Linux / macOS**:
      ```bash
      source venv/bin/activate
      ```

4. **Установите зависимости**:

    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Настройка

1. **Создайте файл `.env`** в корне проекта и добавьте следующие переменные:

    ```env
    DISCORD_BOT_TOKEN=your_bot_token_here
    ```

2. **Настройте `config.py`**, чтобы указать ID каналов, роли и другие параметры

## ▶️ Запуск

1. Убедитесь, что виртуальное окружение активировано.
2. Запустите бота:

    ```bash
    python main.py
    ```


## 📁 Структура проекта

```
helix-bot/
│
├── main.py            # Точка входа в приложение
├── bot_init.py        # Инициализация бота и загрузка Cog'ов
├── config.py          # Конфигурация бота и константы
├── .env               # Переменные окружения
│
├── cogs/
│   ├── __init__.py
│   ├── general_cog.py
│   ├── event_cog.py
│   └── ss14_auth_cog.py # Cog для привязки SS14 аккаунтов
│
├── modules/
│   ├── get_creation_date.py
│   ├── database_manager.py
│   └── check_roles.py
│
└── README.md
```

import disnake
from disnake import TextInputStyle
from disnake.ext import commands, tasks
from disnake.ui import TextInput

from bot_init import cfg, ss14_db
from modules.get_creation_date import get_creation_date


async def get_pinned_message(channel):
    """
    Получает закреплённое сообщение, если оно есть.
    """
    pinned_messages = await channel.pins()
    for message in pinned_messages:
        if message.author == channel.guild.me:
            return message
    return None


class NicknameModal(disnake.ui.Modal):
    def __init__(self):
        components = [
            TextInput(
                label="Введите UID SS14.(UID-ЭТО НЕ ИМЯ АККАУНТА)",
                custom_id="user_id_input",
                style=TextInputStyle.short,
                max_length=50,
            )
        ]
        super().__init__(title="Привязка аккаунта SS14", components=components)

    async def callback(self, inter: disnake.ModalInteraction):
        await inter.response.defer(with_message=False, ephemeral=True)

        user_id_input = inter.text_values["user_id_input"].strip()
        discord_id = str(inter.author.id)
        tech_channel = inter.bot.get_channel(cfg.LOG_TECH_CHANNEL_AUTH_ID)

        if tech_channel is None:
            print("Ошибка: tech_channel не найден. Проверь ID или права доступа.")
            return

        # Проверяем user_id на валидность
        if not user_id_input or not user_id_input.strip():
            await inter.send(
                "❌ Ошибка: User ID не может быть пустым.\n"
                "Пожалуйста, введите ваш User ID.",
                ephemeral=True
            )
            return

        user_id = user_id_input

        # Проверяем, есть ли пользователь в базе по user_id
        player_data = ss14_db.get_username_by_user_id(user_id)
        if not player_data:
            try:
                user = await inter.bot.fetch_user(discord_id)
                await user.send(
                    "❌ Ваш user_id не найден в базе данных. Попробуйте позже!"
                )
                await inter.send(
                    "❌ Ваш user_id не найден в базе данных. Попробуйте позже!",
                    ephemeral=True
                )
            except disnake.Forbidden:
                print(f"⚠️ Не удалось отправить ЛС пользователю {discord_id}")

            await tech_channel.send(
                f"⚠️ Пользователь <@{discord_id}> пытался привязать несуществующий user_id **{user_id}**."
            )
            return

        # Проверка, привязан ли уже
        if ss14_db.is_user_linked(user_id, discord_id):
            try:
                discord_user = await inter.bot.fetch_user(discord_id)
                await discord_user.send(
                    "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна."
                )
                await inter.send(
                    "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна.",
                    ephemeral=True
                )
            except disnake.Forbidden:
                print(f"⚠️ Не удалось отправить ЛС пользователю {discord_id}")

            await tech_channel.send(
                f"⚠️ Пользователь <@{discord_id}> пытался повторно привязать user_id **{user_id}**."
            )
            return

        # if ss14_db.is_user_linked(user_id, discord_id, "dev"):
        #     try:
        #         discord_user = await inter.bot.fetch_user(discord_id)
        #         await discord_user.send(
        #             "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна. DEV"
        #         )
        #         await inter.send(
        #             "❌ Ваш аккаунт уже привязан! Повторная привязка невозможна. DEV",
        #             ephemeral=True
        #         )
        #     except disnake.Forbidden:
        #         print(f"⚠️ Не удалось отправить ЛС пользователю {discord_id}")

        #     await tech_channel.send(
        #         f"⚠️ Пользователь <@{discord_id}> пытался повторно привязать user_id **{user_id}**. DEV"
        #     )
        #     return

        creation_date = get_creation_date(user_id)

        ss14_db.link_user_to_discord(user_id, discord_id)
        # ss14_db.link_user_to_discord(user_id, discord_id, "dev")

        user = await inter.bot.fetch_user(discord_id)
        userNamePlayer = ss14_db.get_username_by_user_id(user_id)

        await tech_channel.send(
            f"✅ **Привязка аккаунта**\n"
            f"> **Discord ID:** {user.name} - {discord_id} \n"
            f"> **SS14 ID:** {userNamePlayer} - `{user_id}`\n"
            f"> **Дата создания аккаунта SS14:** {creation_date}\n"
        )
        await inter.send(
            embed=disnake.Embed(
                title="✅ Привязка завершена!",
                description=f"Ваш SS14 аккаунт {userNamePlayer} user_id **{user_id}** успешно привязан.",
                color=disnake.Color.green(),
            ),
            ephemeral=True
        )


# Класс для кнопки
class RegisterButton(disnake.ui.View):
    """
        Регистрация кнопки
    """
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="🔗 Привязать аккаунт", style=disnake.ButtonStyle.primary)
    async def register(self, button: disnake.ui.Button, inter: disnake.MessageInteraction): # pylint: disable=W0613
        """
            Вызов модального окна
        """
        await inter.response.send_modal(NicknameModal())


class SS14AuthCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.discord_auth_update.start()  # Запускаем задачу при инициализации

    def cog_unload(self):
        # Останавливаем задачу при выгрузке Cog'а
        self.discord_auth_update.cancel()

    @tasks.loop(hours=12)
    async def discord_auth_update(self):
        """
        Задача, выполняющаяся каждые 12 часов.
        Редактирует сообщение и активирует кнопку привязки аккаунта
        Если не находит его, то создаёт новое и закрепляет.
        """
        channel = self.bot.get_channel(cfg.CHANNEL_AUTH_DISCORD_SS14_ID)  # ID канала
        if channel:
            # await channel.purge(limit=10) # удаление 10 сообщений
            embed = disnake.Embed(
                title="🔗 Привязка аккаунта SS14",
                description=(
                    "Для игры на сервере вам необходимо привязать свой аккаунт SS14.\n"
                    "Нажмите кнопку ниже, затем введите UID вашего аккаунта.\n"
                    "UID можно получить в при заходе на сервер."
                ),
                color=disnake.Color.blue(),
            )
            embed.set_footer(
                text="Space Dream SS14",
                icon_url=(
                    "https://media.discordapp.net/attachments/"
                    "1358792797792108724/1431359683997864077/log"
                    "otis.png?ex=68fd2116&is=68fbcf96&hm=0e492d6"
                    "cf0c6002f6c148ba6071a90e43c1b429c7fd3f9632c"
                    "a2e8d6e48f50f9&=&format=webp&quality=lossle"
                    "ss&width=950&height=950"
                )
            )

            message_id = cfg.AUTH_MESSAGE_ID

            try:
                if message_id:
                    old_message = await channel.fetch_message(message_id)
                    await old_message.edit(embed=embed, view=RegisterButton())
                    print(f"✅ Сообщение обновлено Update Discord Auth (ID: {message_id})")
                    return
            except disnake.NotFound:
                print("❌ Старое сообщение не найдено. Создаём новое...")

        # Если сообщение не найдено, ищем в закреплённых
        old_message = await get_pinned_message(channel)
        if old_message:
            await old_message.edit(embed=embed, view=RegisterButton())
            print(f"✅ Используем закреплённое сообщение Update Discord Auth (ID: {old_message.id})")
            return

        # Если старого сообщения нет, отправляем новое
        new_message = await channel.send(embed=embed, view=RegisterButton())
        await new_message.pin()  # Закрепляем его
        print(f"✅ Отправлено новое сообщение Update Discord Auth (ID: {new_message.id})")

    @discord_auth_update.before_loop
    async def before_discord_auth_update(self):
        # Ждём, пока бот будет готов, перед запуском задачи
        await self.bot.wait_until_ready()

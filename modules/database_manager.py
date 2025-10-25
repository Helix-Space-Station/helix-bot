import time
from datetime import datetime

import disnake
import psycopg2


class DatabaseManagerSS14:
    """
    Менеджер для работы с базами данных Space Station 14 (PostgreSQL).
    
    Предоставляет унифицированный интерфейс для работы с основными БД проекта:
    - Основная база данных (main)
    - База данных для разработки (dev)
    
    Attributes
    ----------
    db_params : dict
        Словарь с параметрами подключения к различным БД проекта.
        Содержит конфигурации для 'main' и 'dev' баз данных.
        
    Examples
    --------
    >>> db_manager = DatabaseManagerSS14()
    >>> player_data = db_manager.fetch_player_data("PlayerName")
    """
    def __init__(self, db_configs=None):
        """
        Parameters
        ----------
        db_configs : dict, optional
            Словарь с конфигурациями БД. По умолчанию пустой.
        """
        self.db_params = db_configs or {}
        self.time_zone = None

    def add_database(self, name, db_config):
        """Добавляет конфигурацию базы данных"""
        self.db_params[name] = db_config

    def add_time_zone(self, time_zone):
        if time_zone:
            self.time_zone = time_zone
        else:
            print("Time zone not set")


    def _get_connection(self, db_name='main'):
        """Возвращает соединение с указанной базой данных"""
        if db_name not in self.db_params:
            raise ValueError(f"Unknown database name: {db_name}")

        return psycopg2.connect(**self.db_params[db_name])


    def get_tables_size(self, db_name='main'):
        """
        Возвращает список всех таблиц в базе данных с их размерами и общий объём

        Parameters
        ----------
        db_name : str, optional
            Имя базы данных ('main' или 'dev'), по умолчанию 'main'

        Returns
        -------
        tuple
            (list_of_tables, total_size) где:
            - list_of_tables: список словарей с информацией о таблицах
            - total_size: общий размер всех таблиц в удобочитаемом формате
        """
        query = """
        SELECT 
            table_name,
            pg_size_pretty(pg_total_relation_size(quote_ident(table_name))) as size,
            pg_total_relation_size(quote_ident(table_name)) as size_bytes
        FROM 
            information_schema.tables
        WHERE 
            table_schema = 'public'
        ORDER BY 
            size_bytes DESC;
        """

        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    tables = [
                        {'table': row[0], 'size': row[1]}
                        for row in cursor.fetchall()
                    ]

                    # Получаем общий размер базы
                    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
                    total_size = cursor.fetchone()[0]

                    return tables, total_size
        except Exception as e:
            print(f"Error getting tables size: {e}")
            return [], "0 bytes"


    def fetch_discord_admins(self, db_name='main'):
        """
        Получает список администраторов с привязкой к Discord
        
        Parameters
        ----------
        db_name : str
            Имя базы данных ('main' или 'dev')
            
        Returns
        -------
        list
            Список кортежей (discord_id, game_username, title, rank_name)
        """
        query = """
        SELECT 
            du.discord_id,
            p.last_seen_user_name AS game_username,
            a.title,
            ar.name AS rank_name
        FROM discord_user du
        JOIN player p ON du.user_id = p.user_id
        JOIN admin a ON du.user_id = a.user_id
        LEFT JOIN admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
        ORDER BY p.last_seen_user_name ASC
        """

        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при запросе администраторов: {str(e)}")
            return []


    def check_connection(self, db_name='main') -> tuple[bool, float, str]:
        """
        Проверяет подключение к указанной базе данных и возвращает статус.
        
        Parameters
        ----------
        db_name : str
            Имя базы данных для проверки ('main' или 'dev')
            
        Returns
        -------
        tuple[bool, float, str]
            - bool: Флаг успешного подключения
            - float: Время отклика в миллисекундах
            - str: Сообщение об ошибке (пустая строка при успехе)
        """
        try:
            start_time = time.time()
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
            ping_time = (time.time() - start_time) * 1000
            return True, ping_time, ""
        except Exception as e:
            return False, 0.0, str(e)


    def get_connection_status_report(self) -> str:
        """
        Формирует отчет о состоянии подключений ко всем базам данных.
        
        Returns
        -------
        str
            Отформатированный отчет в виде строки Markdown
        """
        report_lines = ["🔍 **Проверка состояния баз данных:**"]

        for db_name in self.db_params.keys():
            success, ping_time, error = self.check_connection(db_name)
            if success:
                report_lines.append(
                    f"✅ `{db_name}`: Подключение успешно | Пинг: {ping_time:.2f}мс"
                )
            else:
                report_lines.append(
                    f"❌ `{db_name}`: Ошибка подключения - {error}"
                )

        return "\n".join(report_lines)


    def fetch_player_data(self, user_name, db_name='main'):
        """
        Поиск данных игрока по имени пользователя в основной базе или логах подключений.
        
        Осуществляет поиск в следующем порядке:
        1. В таблице player по полю last_seen_user_name
        2. Если не найдено, в таблице connection_log по полю user_name
        
        Parameters
        ----------
        user_name : str
            Имя пользователя для поиска (точное совпадение)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки
        
        Returns
        ----------
        tuple or None
            Возвращает кортеж с данными игрока в зависимости от места нахождения:
            - Если найден в таблице player: 
            (player_id, user_id, first_seen_time, last_seen_user_name)
            - Если найден в таблице connection_log:
            (connection_log_id, user_id, user_name)
            - None если игрок не найден ни в одной таблице
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT player_id, user_id, first_seen_time, last_seen_user_name
                FROM player
                WHERE last_seen_user_name = %s
                """
                cursor.execute(query, (user_name,))
                result = cursor.fetchone()

                # Если не нашли в player, ищем в connection_log
                if result is None:
                    query = """
                    SELECT connection_log_id, user_id, user_name
                    FROM connection_log
                    WHERE user_name = %s
                    """
                    cursor.execute(query, (user_name,))
                    result = cursor.fetchone()

        return result


    def is_user_linked(self, user_id, discord_id, db_name='main'):
        """
        Проверяет, существует ли уже указанный discord_id или user_id в базе данных.
        
        Parameters
        ----------
        user_id : str
            ID пользователя в игровой базе данных
        discord_id : str
            Discord ID пользователя (обычно snowflake ID как строка)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки

        Returns
        ----------
        bool
            True если пользователь уже привязан (найдено совпадение по discord_id или user_id), 
            иначе False
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                # Проверяем, существует ли уже discord_id в базе
                cursor.execute(
                    "SELECT 1 FROM discord_user WHERE discord_id = %s",
                    (str(discord_id),)
                )
                result_discord_id = cursor.fetchone()

                # Проверяем, существует ли уже user_id в базе
                cursor.execute("SELECT 1 FROM discord_user WHERE user_id = %s", (user_id,))
                result_user_id = cursor.fetchone()

                return bool(result_discord_id or result_user_id)


    def link_user_to_discord(self, user_id, discord_id, db_name='main'):
        """
        Функция записи данных о привязке Discord в БД
        
        Parameters
        ----------
        
        user_id : str
            ID пользователя в игровой базе данных
        discord_id : str
            Discord ID пользователя (обычно snowflake ID как строка)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                # Получаем текущий максимум discord_user_id
                cursor.execute("SELECT COALESCE(MAX(discord_user_id), 0) FROM discord_user")
                max_id = cursor.fetchone()[0]
                next_id = max_id + 1

                query = """
                INSERT INTO discord_user (discord_user_id, user_id, discord_id)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (next_id, user_id, discord_id))
            conn.commit()


    def unlink_user_from_discord(self, discord: disnake.Member, db_name='main'):
        """
        Функция отвязки Discord от аккаунта в БД
        
        Parameters
        ----------
        
        user_id : str
            ID пользователя в игровой базе данных
        discord_id : str
            Discord ID пользователя (обычно snowflake ID как строка)
        db_name : str, optional
            Имя базы данных для подключения: 
            - 'main' - основная база (по умолчанию)
            - 'dev' - база разработки

        Returns
        ----------
        str
            user_id если отвязка прошла успешно, иначе None
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "DELETE FROM discord_user WHERE discord_id = %s RETURNING user_id", 
                    (str(discord.id),)
                )
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else None


    def get_user_id_by_discord_id(self, discord_id: str, db_name='main'):
        """
        Получает user_id из игровой базы данных по Discord ID пользователя.

        Производит поиск в указанной базе данных в таблице discord_user,
        возвращая соответствующий user_id для заданного Discord ID.

        Parameters
        ----------
        discord_id : str
            Уникальный идентификатор пользователя Discord (снежинка/Snowflake ID)
            в строковом формате. Пример: "123456789012345678"
        
        db_name : str, optional
            Наименование базы данных для поиска, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - база данных для разработки

        Returns
        -------
        str | None
            Возвращает user_id в виде строки, если запись найдена.
            Возвращает None, если соответствие не найдено.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_id FROM discord_user WHERE discord_id = %s", 
                    (discord_id,))
                result = cursor.fetchone()
                return result[0] if result else None

    def is_admin(self, user_id: int, db_name='main'):
        """
        Проверяет наличие административных прав у пользователя.

        Parameters
        ----------
        user_id : int
            Уникальный идентификатор пользователя в игровой базе данных.
            Должен быть целым числом.
        
        db_name : str, optional
            Наименование базы данных для проверки, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - база данных для разработки

        Returns
        -------
        bool
            True - если пользователь имеет административные права,
            False - если не имеет прав администратора или пользователь не найден.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT 1 FROM admin WHERE user_id = %s", 
                    (user_id,))
                result = cursor.fetchone()
                return result is not None

    def get_username_by_user_id(self, user_id, db_name='main'):
        """
        Получает последний известный никнейм игрока по его уникальному идентификатору.

        Производит поиск в указанной базе данных в таблице player,
        возвращая значение last_seen_user_name для заданного user_id.

        Parameters
        ----------
        user_id : str
            Уникальный идентификатор пользователя в системе.
            Ожидается строковое значение, даже если ID числовой.
        
        db_name : str, optional
            Целевая база данных для поиска, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - тестовая база данных

        Returns
        -------
        str | None
            - Последний известный никнейм пользователя в виде строки, если найден
            - None, если пользователь не найден или произошла ошибка
        """
        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT last_seen_user_name 
                    FROM player 
                    WHERE user_id = %s
                    """
                    cursor.execute(query, (user_id,))
                    result = cursor.fetchone()
                    return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Ошибка при запросе к БД: {e}")
            return None

    def get_user_id_by_username(self, last_seen_user_name, db_name='main'):
        """
        Получает user_id  игрока по его никнейму.

        Производит поиск в указанной базе данных в таблице player,
        возвращая значение user_id для заданного last_seen_user_name.

        Parameters
        ----------
        last_seen_user_name. : str
            Никнейм пользователя в системе.
            Ожидается строковое значение.
        
        db_name : str, optional
            Целевая база данных для поиска, по умолчанию 'main'.
            Допустимые значения:
            - 'main' - основная рабочая база данных
            - 'dev' - тестовая база данных

        Returns
        -------
        str | None
            - user_id пользователя, если найден
            - None, если пользователь не найден или произошла ошибка
        """
        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT user_id 
                    FROM player 
                    WHERE last_seen_user_name = %s
                    """
                    cursor.execute(query, (last_seen_user_name,))
                    result = cursor.fetchone()
                    return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Ошибка при запросе к БД: {e}")
            return None

    def fetch_player_notes_by_username(self, username, db_name='main'):
        """
            Функция получения заметок из БД
        """
        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT 
                        admin_notes.admin_notes_id,
                        admin_notes.created_at,
                        admin_notes.message,
                        admin_notes.severity,
                        admin_notes.secret,
                        admin_notes.last_edited_at,
                        admin_notes.last_edited_by_id,
                        player.player_id,
                        player.last_seen_user_name,
                        admin.created_by_name
                    FROM admin_notes
                    INNER JOIN player ON admin_notes.player_user_id = player.user_id
                    LEFT JOIN (
                        SELECT user_id AS created_by_id, last_seen_user_name AS created_by_name
                        FROM player
                    ) AS admin ON admin_notes.created_by_id = admin.created_by_id
                    WHERE player.last_seen_user_name = %s;
                    """
                    cursor.execute(query, (username,))
                    result = cursor.fetchall()
                    return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе к БД: {e}")
            return None

    def get_baninfo_by_ban_id(self, ban_id, db_name='main'):
        """
            Возращает информацию о бане по айди бана
        Args:
            ban_id (str): Айди бана
            db_name (str, optional): Имя базы данных ('main' или 'dev'), по умолчанию 'main'
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT player_user_id, address, ban_time, expiration_time, reason, banning_admin, round_id
                FROM server_ban
                WHERE server_ban_id = %s
                """
                cursor.execute(query, (ban_id,))
                result = cursor.fetchone()
                return result

    def fetch_banlist_by_username(self, username, db_name='main'):
        """
            Возращает информацию об истории банов игрока по игровому никнейму
        """
        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT 
                        sb.server_ban_id, 
                        sb.ban_time, 
                        sb.expiration_time, 
                        sb.reason, 
                        COALESCE(p.last_seen_user_name, 'Неизвестно') AS admin_nickname,
                        ub.unban_time,
                        COALESCE(p2.last_seen_user_name, 'Неизвестно') AS unban_admin_nickname
                    FROM server_ban sb
                    LEFT JOIN player p ON sb.banning_admin = p.user_id
                    LEFT JOIN server_unban ub ON sb.server_ban_id = ub.ban_id
                    LEFT JOIN player p2 ON ub.unbanning_admin = p2.user_id
                    WHERE sb.player_user_id = (
                        SELECT user_id FROM player WHERE last_seen_user_name = %s
                    )
                    ORDER BY sb.server_ban_id ASC
                    """
                    cursor.execute(query, (username,))
                    result = cursor.fetchall()
                    return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе к БД: {e}")
            return None

    def pardon_ban(
        self,
        ban_id: int,
        admin_user_id: str,
        db_name: str = 'main'
        ) -> tuple[bool, str]:
        """
        Снимает бан с указанным ID и записывает информацию о разбане в БД.

        Parameters
        ----------
        ban_id : int
            ID бана для снятия
        admin_user_id : str
            UUID администратора, снимающего бан
        db_name : str, optional
            Имя базы данных ('main' или 'dev'), по умолчанию 'main'

        Returns
        -------
        tuple[bool, str]
            Кортеж с результатом операции:
            - bool: Флаг успешного выполнения
            - str: Сообщение о результате
        """
        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    # Проверка существования бана
                    cursor.execute(
                        "SELECT 1 FROM server_ban WHERE server_ban_id = %s", 
                        (ban_id,)
                    )
                    if not cursor.fetchone():
                        return False, f"❌ Ошибка: Бан с ID `{ban_id}` не существует."

                    # Проверка, не снят ли уже бан
                    cursor.execute(
                        "SELECT 1 FROM server_unban WHERE ban_id = %s", 
                        (ban_id,)
                    )
                    if cursor.fetchone():
                        return False, f"⚠️ Бан с ID `{ban_id}` уже был снят ранее."

                    # Получение имени администратора
                    cursor.execute(
                        "SELECT last_seen_user_name FROM player WHERE user_id = %s",
                        (admin_user_id,)
                    )
                    admin_data = cursor.fetchone()

                    if not admin_data:
                        return False, (
                            f"❌ Ошибка: Администратор с user_id `{admin_user_id}` "
                            "не найден в базе игроков."
                        )

                    admin_name = admin_data[0]

                    # Получение текущего времени (MSK)
                    unban_time = (
                        datetime
                        .now(self.time_zone)
                        .strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + " +0300"
                    )

                    # Запись в server_unban
                    cursor.execute(
                        """
                        INSERT INTO server_unban (ban_id, unbanning_admin, unban_time)
                        VALUES (%s, %s, %s::timestamptz)
                        """,
                        (ban_id, admin_user_id, unban_time)
                    )
                    conn.commit()

                    return True, (
                        f"✅ Бан с ID `{ban_id}` успешно снят "
                        f"администратором `{admin_name}`."
                    )

        except psycopg2.Error as e:
            conn.rollback()
            raise RuntimeError(f"Ошибка базы данных при снятии бана: {e}") from e


    def fetch_admin_info(self, nickname, db_name='main'):
        """
        Получает информацию об администраторе по нику.
        
        Parameters
        ----------
        nickname : str
            Никнейм администратора.
        db_name : str, optional
            Название сервера ('main' или 'dev').
        
        Returns
        -------
        tuple or None
            (title, rank_name) если админ найден, иначе None.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT a.title, ar.name
                FROM public.admin a
                JOIN public.admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
                JOIN public.player p ON a.user_id = p.user_id
                WHERE p.last_seen_user_name ILIKE %s
                """
                cursor.execute(query, (nickname,))
                return cursor.fetchone()

    def get_user_id_admin_by_username(self, nickname, db_name='main'):
        """
        Возращает user_id администратора по его нику
        Args:
            nickname (str): Игровой никнейм администратора.
            db_name (str, optional): Имя БД. Defaults to 'main'.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT a.user_id FROM public.admin a
                JOIN public.player p ON a.user_id = p.user_id
                WHERE p.last_seen_user_name ILIKE %s
                """
                cursor.execute(query, (nickname,))
                result = cursor.fetchone()

                return result

    def fetch_admin_rank(self, admin_rank, db_name='main'):
        """
        Метод для получения id админ ранга по его имени
        Args:
            admin_rank (str):
            db_name (str, optional): Название БД в которую мы делаем запрос. Defaults to 'main'.
        Returns:
            Выводит admin_rank_id, или None если такого не нашёл
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT admin_rank_id
                FROM public.admin_rank
                WHERE name ILIKE %s
                """
                cursor.execute(query, (admin_rank,))
                result = cursor.fetchone()

                return result

    def fetch_admin_ranks(self, db_name='main'):
        """
        Возращает список админ рангов на МРП или Дев сервере
        Args:
            db_name (str, optional): Имя БД к которой мы делаем запрос. Defaults to 'main'.
        Returns:
            list: Возращает отсортированный список админ рангов с их айди и именем
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT admin_rank_id, name
                FROM public.admin_rank ORDER BY admin_rank_id ASC
                """
                cursor.execute(query)
                result = cursor.fetchall()

                return result

    def fetch_admins(self, db_name='main'):
        """
            Функция запроса списка администраторов из базы данных
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                # SQL-запрос с привязкой к Discord
                query = """
                SELECT 
                    p.last_seen_user_name, 
                    a.title, 
                    ar.name, 
                    du.discord_id
                FROM public.admin a  
                JOIN public.admin_rank ar ON a.admin_rank_id = ar.admin_rank_id
                LEFT JOIN public.player p ON a.user_id = p.user_id
                LEFT JOIN public.discord_user du ON a.user_id = du.user_id
                ORDER BY p.last_seen_user_name ASC
                """
                cursor.execute(query)
                admins = cursor.fetchall()

                return admins

    def permission_add_admin(self, user_id, title, rank, db_name='main'):
        """
        С помощью INSERT добавляет нового администратора в таблицу
        Тем самым выдавая ему права
        Args:
            user_id (str): user_id пользователя сс14
            title (str): Подпись администратора
            rank (str): Id админ ранга
            db_name (str, optional): Имя БД. Defaults to 'main'.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                INSERT INTO
                public.admin (user_id, title, admin_rank_id)
                VALUES (%s, %s, %s)
                """
                cursor.execute(query, (user_id, title, rank))

    def permission_tweak_admin(self, title, rank, user_id, db_name='main'):
        """
        Изменяет обновляет права администратору
        Args:
            title (str): Подпись администратора
            rank (str): Id админ ранга
            user_id (str): user_id пользователя сс14
            db_name (str, optional): Имя БД. Defaults to 'main'.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                UPDATE public.admin
                SET title = %s, admin_rank_id = %s WHERE user_id = %s
                """
                cursor.execute(query, (title, rank, user_id))

    def permission_delete_admin(self, admin_id, db_name='main'):
        """
        Удаляет администратора из таблицы по его user_id
        Args:
            admin_id (str): admin_id пользователя сс14
            db_name (str, optional): Имя БД. Defaults to 'main'.
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                DELETE FROM public.admin
                WHERE user_id = %s
                """
                cursor.execute(query, (admin_id,))

    def fetch_uploads(self, db_name='main'):
        """
        Получает информацие логов загрузок .ogg файлов

        Parameters
        ----------
        db_name : str, optional
            Имя базы данных ('main' или 'dev'), по умолчанию 'main'
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT ul.uploaded_resource_log_id, ul.date, p.last_seen_user_name, ul.path
                FROM public.uploaded_resource_log ul
                LEFT JOIN public.player p ON ul.user_id = p.user_id
                ORDER BY ul.date DESC
                """
                cursor.execute(query)
                return cursor.fetchall()


    def fetch_profiles_by_nickname(self, nickname, db_name='main'):
        """
        Получает информацие о игровых персонажах игрока по его нику

        Parameters
        ----------
        db_name : str, optional
            Имя базы данных ('main' или 'dev'), по умолчанию 'main'
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT p.profile_id, p.preference_id, p.char_name, p.age, p.gender, p.species
                FROM profile p
                WHERE p.preference_id IN (
                    SELECT pr.preference_id
                    FROM preference pr
                    WHERE pr.user_id IN 
                    (SELECT pl.user_id FROM player pl WHERE pl.last_seen_user_name = %s)
                )
                ORDER BY p.profile_id ASC
                """
                cursor.execute(query, (nickname,))
                result = cursor.fetchall()
                return result if result else None

    def get_player_timestats_by_username(self, username, db_name='main'):
        """
            Функция для получения статистики времени игрока
        """
        try:
            with self._get_connection(db_name) as conn:
                with conn.cursor() as cursor:
                    query = """
                    SELECT 
                        play_time.tracker,
                        play_time.time_spent
                    FROM player
                    INNER JOIN play_time ON player.user_id = play_time.player_id
                    WHERE player.last_seen_user_name = %s;
                    """
                    cursor.execute(query, (username,))
                    result = cursor.fetchall()
                    return result
        except psycopg2.Error as e:
            print(f"Ошибка при запросе к БД: {e}")
            return None

    def fetch_username_by_char_name(self, char_name, db_name='main'):
        """
        Получает список ников игроков по имени игрового персонажа

        Parameters
        ----------
        char_name : str
            Имя игрового персонажа (может быть у нескольких игроков)
        db_name : str, optional
            Имя базы данных ('main' или 'dev'), по умолчанию 'main'
        
        Returns
        -------
        list of str or None
            Список ников игроков или None, если персонажи с таким именем не найдены
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT pl.last_seen_user_name
                FROM player pl
                WHERE pl.user_id IN (
                    SELECT pr.user_id
                    FROM preference pr
                    WHERE pr.preference_id IN (
                        SELECT p.preference_id
                        FROM profile p
                        WHERE p.char_name = %s
                    )
                )
                ORDER BY pl.last_seen_user_name ASC
                """
                cursor.execute(query, (char_name,))
                result = cursor.fetchall()
                return [row[0] for row in result] if result else None


    def fetch_profile_by_id(self, profile_id, db_name='main'):
        """
        Получает информацие о игровых персонажах игрока по его нику

        Parameters
        ----------
        db_name : str, optional
            Имя базы данных ('main' или 'dev'), по умолчанию 'main'
        """
        with self._get_connection(db_name) as conn:
            with conn.cursor() as cursor:
                query = """
                SELECT 
                    p.profile_id, p.slot, p.char_name, p.age, p.sex, p.hair_name, p.hair_color,
                    p.facial_hair_name, p.facial_hair_color, p.eye_color, p.skin_color, 
                    p.pref_unavailable, p.preference_id, p.gender, p.species, p.markings,
                    p.flavor_text, p.voice, p.erpstatus, p.spawn_priority, p.bark_pitch,
                    p.bark_proto, p.high_bark_var, p.low_bark_var
                FROM profile p
                WHERE p.profile_id = %s
                """
                cursor.execute(query, (profile_id,))
                result = cursor.fetchone()
                return result if result else None

from typing import Callable

import telebot

from .. import utils
from . import commands, uploads
from ..logger import logger

class BotManager:
    def __init__(self) -> None:
        self.status = False
        self.block_turn = None
    
    def add_func(self, func: Callable) -> None:
        self.block_turn = func
    
    def init_bot(self, bot: any) -> None:
        self.bot = bot

    def run(self) -> None:
        logger.log("Bot started!")
        self.status = True
        try:
            self.bot.bot.infinity_polling(skip_pending=True)
            logger.log("The bot has stopped.", 2)
            self.status = False
            return self.block_turn(False, True)
        except Exception as e:
            logger.log("The bot has stopped.", 2)
            error = str(e)
            print(error)
            if error.endswith("Description: Unauthorized") or error == "Bot token is not defined":
                logger.log("Invalid token.", 3)
            if error.endswith('([Errno 11001] getaddrinfo failed)"))'):
                logger.log("No internet connection.", 3)
            else:
                logger.log("Restarting the bot...")
                return self._run()
            self.status = False
            return self.block_turn(False, True)
    
    def stop(self) -> None:
        if self.status:
            logger.log("Stopping the bot...")
            self.status = False
            self.bot.bot.stop_polling()
    
    def get_status(self) -> bool:
        return self.status
    
    def handle(self, exception) -> bool:
        excep = str(exception)
        if excep.endswith("Read timed out. (read timeout=25)"):
            logger.log("Internet connection lost.", 3)
            return False
        if excep.endswith('([Errno 11001] getaddrinfo failed)"))'):
            return False
        logger.log(excep, 3)
        return True

manager = BotManager()

class YawBot:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.shortcuts = utils.load_json("config/shortcuts.json")

        logger.log("Initializing the bot...")
        token = self.config["token"]
        self.uid = self.config["uid"]
        self.bot = telebot.TeleBot(token, "HTML", skip_pending=True, exception_handler=manager, allow_sending_without_reply=True, threaded=False)

        logger.log("Initialization of handlers...", 0)
        self.commands = commands.Commands(self.bot, self.shortcuts)
        self.Uploads = uploads.Uploads(self.bot)
        self.bot.message_handler(func=lambda message: not message.from_user.is_bot)(self.handle_commands)

        self.register_handlers()

        logger.log("Initialization complete!")
    
    def register_handlers(self) -> None:
        self.bot.message_handler(content_types=["voice"])(self.Uploads.handle_voice)
        self.bot.message_handler(content_types=["audio"])(self.Uploads.handle_audio)
        self.bot.message_handler(content_types=["document"])(self.Uploads.handle_document)
        self.bot.message_handler(content_types=["video", "video_note"])(self.Uploads.handle_video)
        self.bot.message_handler(content_types=["photo"])(self.Uploads.handle_photo)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith("fastrun_"))(self.commands.fastrun_callback)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith("removeadm_"))(self.removeadm_callback)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith("removepath_"))(self.commands.removepath_callback)

    def handle_commands(self, message: telebot.types.Message):
        cmd = message.text.split(" ")[0].lower()
        if not cmd.startswith("/"):
            return
        uid = message.chat.id
        admin = uid == self.uid
        in_admins = admin or uid in self.config["users"].values()

        if in_admins:
            self.admin_commands(message, cmd, admin)
        else:
            if cmd == "/entercode":
                self.handle_entercode(message)
            else:
                self.bot.send_message(message.chat.id, f"<b>У вас нет доступа к этому боту или команде.</b>\n<i>Ваш UID:</i> <code>{message.from_user.id}</code>")
    
    def admin_commands(self, message: telebot.types.Message, cmd: str, admin: bool):
        if cmd == "/start":
            self.handle_start(message)
        elif cmd in self.commands.cmd_dict.keys():
            self.commands.cmd_dict[cmd](message)
            logger.log(f"{message.from_user.username}({message.from_user.id}) use command {message.text}")
        elif admin and cmd in ["/changepass", "/setadmcount", "/checkadm"]:
            if cmd == "/changepass":
                self.handle_changepass(message)
            elif cmd == "/setadmcount":
                self.handle_setadmcount(message)
            elif cmd == "/checkadm":
                self.handle_checkadm(message)
            logger.log(f"ADMIN use command {message.text}", 2)

    def handle_changepass(self, message: telebot.types.Message):
        password = message.text[12:]
        if password:
            self.config["password"] = password
            msg = "<b>Пароль сохранён.</b>\nТеперь новые пользователи смогут получить доступ к боту через команду <code>/entercode &lt;код&gt;</code>."
        else:
            self.config["password"] = ""
            msg = "<b>Пароль удалён.</b> Теперь новые пользователи не смогут получить доступ к боту."
        utils.save_json("config/config.json", self.config)
        self.bot.send_message(message.chat.id, msg)
    
    def handle_setadmcount(self, message: telebot.types.Message):
        msg_split = message.text.split(" ")
        count = utils.arg_to_time(msg_split)
        now_count = len(self.config["users"])
        if count > 0:
            if now_count > count:
                msg = f"""В данный момент <b>{now_count}</b> пользователей имеют доступ к боту.
Чтобы установить ограничение в <b>{count}</b> пользователей, удалите <b>{now_count-count}</b> пользователей через команду /checkadm."""
            else:
                self.config["max_users"] = count
                utils.save_json("config/config.json", self.config)
                msg = f"Установлено ограничение в <b>{count}</b> пользователей."
        else:
            msg = """Вы не можете установить ограничене в <b>0</b> пользователей.
Чтобы отключить функцию выдачи доступа пропишите, <i>без аргументов</i>, команду /changepass"""
        self.bot.send_message(message.chat.id, msg)
    
    def handle_checkadm(self, message: telebot.types.Message):
        users = self.config["users"]
        if len(users) > 0:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for user in users.keys():
                btn = telebot.types.InlineKeyboardButton(f"{user} ({users[user]})", callback_data=f"removeadm_{users[user]}")
                keyboard.add(btn)
            self.bot.send_message(message.chat.id, "Выберите, какого пользователя вы хотите <b>удалить</b>.", reply_markup=keyboard)
        else:
            self.bot.send_message(message.chat.id, "Дополнительные пользователи бота <b>отсутсвуют</b>.")
    
    def removeadm_callback(self, call: telebot.types.CallbackQuery):
        uid = int(call.data[10:])
        users = self.config["users"]
        if uid in users.values():
            key = [user for user, uid_ in users.items() if uid_ == uid][0]
            users.pop(key)
            self.config["users"] = users
            msg = "Пользователь <b>удалён</b>."
        else:
            msg = "<i>Пользователь не найден</i>."
        self.bot.send_message(call.from_user.id, msg)
    
    def handle_entercode(self, message: telebot.types.Message):
        password = message.text[11:]
        real_pass = self.config["password"]
        if password:
            if real_pass and len(self.config["users"]) < self.config["max_users"]:
                if password == real_pass:
                    self.config["users"][utils.get_username(message)] = message.from_user.id
                    utils.save_json("config/config.json", self.config)
                    msg = "Вы ввели <b>правильный код</b>. Теперь у вас есть <i>частичный доступ</i> к боту."
                    logger.log(f"{message.from_user.username}({message.from_user.id}) has entered the correct access code for the bot.", 2)
                else:
                    msg = "<i>Вы ввели неправильный код.</i>"
                    logger.log(f"{message.from_user.username}({message.from_user.id}) attempted to enter an access code for the bot.", 2)
            else:
                msg = "<i>Владелец бота</i> <b>отключил</b> <i>или</i> <b>ограничил</b> <i>функцию выдачи доступа другим пользователям</i>."
        else:
            msg = "<i>Введите код доверия для получения доступа к боту.</i>"
        self.bot.send_message(message.chat.id, msg)

    def handle_start(self, message: telebot.types.Message):
        btns = ["/status", "/shutdown", "/lock", "/sleep", "/reboot", "/waitbreak", "/screenshot", 
          "/record", "/setvolume", "/workload", "/processes", "/fastrun", "/removepath"]
        msg = f"""<b>Yaw v2.0</b>
<i>Я ваш личный бот для управления ПК с помощью Телеграмма!</i>
<b>Ваш UID:</b> <code>{message.from_user.id}</code>

<b>Доступные команды:</b>
<b>/status</b> - Проверяет статус ПК. <i>нет ответа - ПК выключен</i>

<b>/shutdown &lt;время, сек&gt;</b> - Полностью выключает ПК и бота через указанный промежуток времени. <i>Если промежуток не указан - выключается сразу</i>
<b>/lock</b> - Блокирует ПК без выключения
<b>/sleep</b> - Вводит ПК в режим сна
<b>/reboot &lt;время, сек&gt;</b> - Перезапускает ПК через указанный промежуток времени. <i>Если промежуток не указан - перезапускает сразу</i>
<b>/waitbreak</b> - Отменяет перезапуск или выключение ПК

<b>/screenshot</b> - Отправляет снимок экрана ПК
<b>/record &lg;время, сек&gt;</b> - Начинает запись микрофона на указанное время. <i>Если время не указано - 30 секунд</i>

<b>/setvolume &lt;громкость&gt;</b> - Устанавливает на ПК указанную громкость в процентах. <i>Если громкость не указана - 0%</i>

<b>/workload</b> - Выводит данные загруженности процессора и оперативной памяти
<b>/processes</b> - Выводит список запущенных процессов

<b>Запуск файлов:</b>
<b>/runfile &lt;полный путь&gt;</b> - Запускает файл по указанному пути
<b>/savepath &lt;имя ярлыка без пробелов&gt; &lt;полный путь&gt;</b> - Сохраняет ярлык для быстрого запуска файлов
<b>/fastrun &lt;имя ярлыка&gt;</b> - Запускает файл по сохранённому ранее пути
<b>/removepath &lt;имя ярлыка&gt;</b> - Удаляет указанный ярлык

<b>Управление консолью:</b>
<b>/cmd &lt;команда&gt;</b> - Вводит указанную команду в консоль
<b>/cd &lt;путь до папки&gt;</b> - Меняет рабочий каталог для /cmd
"""
        if message.chat.id == self.uid:
            msg += """
<b>Выдача доступа к боту</b> <i>(Только вы имеете доступ к этим командам)</i><b>:</b>
<b>/changepass &lt;пароль&gt;</b> - Меняет пароль для получения доступа к боту. <i>Не указывайте пароль, если хотите отключить эту функцию</i>
<b>/setadmcount &lt;кол-во&gt;</b> - Устанавливает максимальное кол-во пользователей, которые могут получить доступ к боту
<b>/checkadm</b> - Выводит никнеймы пользователей, которые имеют доступ к боту. Также это меню для удаления доступа к боту у конкретных пользователей

<b>/entercode &lt;пароль&gt;</b> - Команда только для пользователей, которые не имеют доступа к боту. <i>Если указан верный пароль, выдаёт доступ к боту</i>
"""
            btns.append("/checkadm")
        keyboard = telebot.types.ReplyKeyboardMarkup()
        for btn in btns:
            btn = telebot.types.KeyboardButton(btn)
            keyboard.add(btn)
        self.bot.send_message(message.chat.id, msg, reply_markup=keyboard)
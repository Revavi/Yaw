# PC REMOTE CONTROL BOT V1.3
# authors: Revavi, msihek
import telebot

import utils
from commands import Commands

class PCRCBot:
	def __init__(self) -> None:
		self.config = utils.load_json("config.json")
		self.shortcuts = utils.load_json("shortcuts.json")

		print("Initializing the bot...")
		token = self.config["token"]
		self.uid = self.config["uid"]
		self.bot = telebot.TeleBot(token)

		print("Command Initialization...")
		self.commands = Commands(self.bot, self.shortcuts)
		self.bot.message_handler()(self.handle_commands)
		self.bot.callback_query_handler(func=lambda call: call.data.startswith("fastrun_"))(self.fastrun_callback)
		print("Initialization complete!")

	def fastrun_callback(self, call) -> None:
		msg = utils.run_shortcut(call.data[8:], self.shortcuts)
		self.bot.send_message(call.from_user.id, msg)

	def handle_commands(self, message) -> None:
		cmd = message.text.split(" ")[0].lower()
		if message.from_user.id == self.uid:
			if cmd == "/start":
				self.handle_start(message)
			elif cmd in self.commands.cmd_dict.keys():
				self.commands.cmd_dict[cmd](message)
		else:
			self.bot.send_message(message.chat.id, f"У вас нет доступа к этому боту или команде.\nВаш UID: {message.from_user.id}")

	def handle_start(self, message) -> None:
		btns = ["/status", "/shutdown", "/lock", "/sleep", "/reboot", "/waitbreak", "/screenshot", "/workload", "/processes",]
		keyboard = telebot.types.ReplyKeyboardMarkup()
		for btn in btns:
			btn = telebot.types.KeyboardButton(btn)
			keyboard.add(btn)
		self.bot.send_message(message.chat.id, f""" PC Remote Control Bot v1.3
Я ваш личный бот для управления ПК с помощью телеграмма!
Ваш UID: {message.from_user.id}

Доступные команды:
/status - проверяет статус ПК (нет ответа - ПК выключен)

/shutdown <время, сек> - полностью выключает ПК и бота через указанный промежуток времени. Если промежуток не указан - выключается сразу.
/lock - блокирует ПК без выключения
/sleep - вводит ПК в режим сна
/reboot <время, сек> - перезапускает ПК через указанный промжетуок времени. Если промежуток не указан - перезапускает сразу.
/waitbreak - отменяет перезапуск или выключение ПК

/screenshot - отправляет снимок экрана ПК

/workload - выводит данные загруженности процессора и оперативной памяти
/processes - выводит список запущенных процессов

Запуск файлов:
/runfile <полный путь> - запускает файл по указанному пути
/savepath <имя ярлыка без пробелов> <полный путь> - сохраняет ярлык для быстрого запуска файлов
/fastrun <имя ярлыка> - запускает файл по сохранённому ранее пути

Управление консолью:
/cmd <команда> - вводит указанную команду в консоль
/cd <путь до папки> - меняет рабочий каталог для /cmd
""", reply_markup=keyboard)

	def run(self) -> None:
		cmds = [("/start", "Информация о боте"), ("/status", "Проверить статус ПК"), ("/shutdown", "Выключить ПК"), ("/lock", "Заблокировать ПК"), ("/reboot", "Перезапуск ПК"),
		  ("/sleep", "Ввести ПК в режим сна"), ("/waitbreak", "Отмена выключения/перезапуска"), ("/workload", "Проверить загруженность ПК"),
		  ("/processes", "Выводит список активных процессов"), ("/runfile", "Запуск файла"), ("/savepath", "Сохранение ярлыка"), ("/fastrun", "Запуск ярлыка"),
		  ("/cmd", "Ввести команду в консоль"), ("/cd", "Изменить рабочую категорию"), ("/kill", "Завершить процесс"), ("/screenshot", "Получить снимок экрана")]
		commands = []
		for cmd in cmds:
			commands.append(telebot.types.BotCommand(cmd[0], cmd[1]))
		self.bot.set_my_commands(commands)

		print("Bot started!")
		try:
			self.bot.polling(non_stop=True)
		except Exception as e:
			print(f"ERROR: {e}\nRestarting the bot...")
			return self.run()
		
if __name__ == "__main__":
	app_class = PCRCBot()
	app_class.run()
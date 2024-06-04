import os
import json
import signal

import psutil
import pyautogui

import utils

class Commands:
	def __init__(self, bot, shortcuts) -> None:
		self.processes = {}
		self.wait_off = False
		self.current_dir = ""
		self.shortcuts = shortcuts

		self.bot = bot
		self.cmd_dict = {
			"/sleep": self.handle_sleep,
			"/lock": self.handle_lock,
			"/status": lambda message: self.bot.send_message(message.chat.id, "ПК включен."),
			"/workload": self.handle_workload,
			"/screenshot": self.handle_screenshot,
			"/shutdown": self.handle_shutdown,
			"/cmd": self.handle_cmd,
			"/cd": self.handle_cd,
			"/waitbreak": self.handle_waitbreak,
			"/reboot": self.handle_reboot,
			"/runfile": self.handle_runfile,
			"/savepath": self.handle_savepath,
			"/fastrun": self.handle_fastrun,
			"/kill": self.handle_kill,
			"/processes": self.handle_processes
		}
	
	def handle_sleep(self, message) -> None:
		self.bot.send_message(message.chat.id, "Перевожу ПК в режим сна...")
		os.system("Rundll32.exe powrprof.dll,SetSuspendState Sleep")
	
	def handle_lock(self, message) -> None:
		os.system("Rundll32.exe user32.dll,LockWorkStation")
		self.bot.send_message(message.chat.id, "ПК заблокирован.")
	
	def handle_workload(self, message) -> None:
		cpu_percent = psutil.cpu_percent()
		ram_percent = psutil.virtual_memory().percent
		ram_total = round(psutil.virtual_memory().total / (1024 **3))
		ram_used = round(psutil.virtual_memory().used / (1024 **3), 1)
		self.bot.send_message(message.chat.id, f"Загруженность ПК:\nCPU: {cpu_percent}%\nRAM: {ram_used}GB/{ram_total}GB ({ram_percent}%)")
	
	def handle_screenshot(self, message) -> None:
		self.bot.send_photo(message.chat.id, pyautogui.screenshot())
	
	def handle_shutdown(self, message) -> None:
		msg = "Выключаю ПК..."
		msg_split = message.text.split(" ")
		t = utils.arg_to_time(msg_split)
		if t > 0:
			msg = f"ПК выключится через {t} секунд...\nВы можете отменить выполнение команды, используя /waitbreak"
		self.bot.send_message(message.chat.id, msg)
		self.wait_off = True
		os.system(f"shutdown /s /t {t}")
	
	def handle_cmd(self, message) -> None:
		command = message.text[5:]
		if command:
			try:
				if self.current_dir:
					os.chdir(self.current_dir)
				output = os.popen(command).read()
				msgs = utils.split_output(output)
				for msg in msgs:
					self.bot.send_message(message.chat.id, msg)
				return
			except Exception as e:
				msg = f"Ошибка: {str(e)}"
		else:
			msg = "Пожалуйста, укажите команду."
		self.bot.send_message(message.chat.id, msg)
	
	def handle_cd(self, message) -> None:
		path = message.text[4:]
		if path:
			try:
				os.chdir(path)
				self.current_dir = path
				msg = f"Рабочий каталог изменен на: {path}"
			except Exception as e:
				msg = f"Ошибка: {str(e)}"
		else:
			msg = "Пожалуйста, укажите путь."
		self.bot.send_message(message.chat.id, msg)
	
	def handle_waitbreak(self, message) -> None:
		msg = "Перезапуск/выключение ПК отменено."
		if self.wait_off:
			os.system("shutdown /a")
		else:
			msg = "Вы не прописывали команду /shutdown или /reboot."
		self.bot.send_message(message.chat.id, msg)
	
	def handle_reboot(self, message) -> None:
		msg = "Перезапускаю ПК..."
		msg_split = message.text.split(" ")
		t = utils.arg_to_time(msg_split)
		if t > 0:
			msg = f"ПК перезапустится через {t} секунд...\nВы можете отменить выполнение команды, используя /waitbreak"
		self.bot.send_message(message.chat.id, msg)
		self.wait_off = True
		os.system(f"shutdown /g /t {t}")
	
	def handle_runfile(self, message) -> None:
		msg = utils.run_file(message.text[9:])
		self.bot.send_message(message.chat.id, msg)
	
	def handle_savepath(self, message) -> None:
		msg_split = message.text.split(" ")
		if len(msg_split) <3:
			return self.bot.send_message(message.chat.id, "Пожалуйста, укажите имя ярлыка без пробелов и путь до файла по формату:\n/savepath <имя ярлыка> <полный путь>")
		
		shortcut_name = msg_split[1]
		file_path = " ".join(msg_split[2:])
		if os.access(file_path, os.X_OK):
			self.shortcuts[shortcut_name] = file_path
			with open("shortcuts.json", mode="w") as f:
				json.dump(self.shortcuts, f, indent=4)
			msg = f"Ярлык {shortcut_name} сохранён."
		else:
			msg = f"Файл {file_path} не является исполняемым."
		self.bot.send_message(message.chat.id, msg)
	
	def handle_fastrun(self, message) -> None:
		chat_id = message.chat.id
		shortcut = message.text[9:]
		keyboard = utils.find_shortcuts(self.shortcuts)
		if not keyboard:
			return self.bot.send_message(chat_id, "У вас нет ярлыков.")
		if shortcut:
			try:
				self.shortcuts[shortcut]
			except KeyError:
				return self.bot.send_message(chat_id, f"Ярлык {shortcut} не найден.", reply_markup=keyboard)
			msg = utils.run_shortcut(shortcut, self.shortcuts)
			self.bot.send_message(chat_id, msg)
		else:
			self.bot.send_message(chat_id, "Пожалуйста, укажите имя ярлыка.", reply_markup=keyboard)
		
	def handle_kill(self, message) -> None:
		pid = message.text[6:]
		if pid:
			data, result = utils.check_pid(pid, self.processes)
			if result:
				pid = int(pid)
				os.kill(pid, signal.SIGTERM)
				self.processes = {}
				msg = f"Процесс {data} завершён.\nПропишите /processes чтобы проверить выполнение команды или отключить другой процесс."
			else:
				msg = data
		else:
			msg = "Пожалуйста, укажите PID процесса."
		self.bot.send_message(message.chat.id, msg)

	def handle_processes(self, message) -> None:
		msg = """
Чтобы завершить процесс напишите: /kill <pid>
Пример: /kill 3301
Если завершите процесс "cmd.exe", то бот выключится.

Активные процессы:
"""
		ignor = ["System Idle Process", "System", "Registry", "smss.exe", "lsass.exe", "csrss.exe", "fontdrvhost.exe", "wininit.exe", "services.exe",
				  "TextInputHost.exe", "RuntimeBroker.exe", "MemCompression", "spoolsv.exe", "mDNSResponder.exe", "WXCastService.exe", "MsMpEng.exe",
				  "SearchIndexer.exe", "dwm.exe", "taskhostw.exe", "dllhost.exe", "conhost.exe", "AggregatorHost.exe", "SgrmBroker.exe", "ShellExperienceHost.exe",
				  "winlogon.exe", "CompPkgSrv.exe", "powershell.exe", "nvsphelper64.exe", "NisSrv.exe", "UserOOBEBroker.exe", "StartMenuExperienceHost.exe",
				  "SystemSettings.exe", "audiodg.exe", "LockApp.exe", "CalculatorApp.exe", "SearchProtocolHost.exe", "sihost.exe", "SearchApp.exe", "explorer.exe",
				  "SearchFilterHost.exe", "ApplicationFrameHost.exe", "smartscreen.exe", "svchost.exe", "WmiPrvSE.exe", "PhoneExperienceHost.exe", "TiWorker.exe",
				  "TrustedInstaller.exe", "MoUsoCoreWorker.exe"]
		self.processes = {}
		for p in psutil.process_iter():
			name = p.name()
			pid = p.pid
			if name not in ignor and name not in self.processes.values():
				msg += f"\n{name} (pid: {pid})"
				self.processes[pid] = name
		self.bot.send_message(message.chat.id, msg)
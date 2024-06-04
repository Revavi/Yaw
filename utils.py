import io
import json
import os
import subprocess

import telebot

def arg_to_time(splitted: list):
	t = 0
	if len(splitted) > 1: 
		t = splitted[1]
		try:
			t = round(int(t))
			if t < 1:
				t = 0
		except ValueError:
			t = 0
	return t

def find_shortcuts(shortcuts) -> telebot.types.InlineKeyboardMarkup | None:
	keyboard = None
	if len(shortcuts) > 0:
		keyboard = telebot.types.InlineKeyboardMarkup()
		for shortcut in shortcuts.keys():
			btn = telebot.types.InlineKeyboardButton(f"{shortcut}", callback_data=f"fastrun_{shortcut}")
			keyboard.add(btn)
	return keyboard

def load_json(path, from_self: bool=False) -> dict:
	if from_self:
		with io.BytesIO() as file:
			file.write(open(path, "rb").read())
			return json.load(file)
	else:
		print(f"Loading {path}...")
		with open(path, encoding="utf-8") as f:
			return json.load(f)

def run_file(path: str=None) -> str:
	if path:
		if os.access(path, os.X_OK):
			try:
				subprocess.run([path], check=True)
				path = path.split("\\")[-1:][0]
				return f"Файл {path} Запущен."
			except subprocess.CalledProcessError as e:
				return f"Ошибка при запуске файла: {e}"
		else:
			return f"Файл {path} не является исполняемым."
	else:
		return "Пожалуйста, укажите путь до файла."

def run_shortcut(shortcut, shortcuts) -> str:
	try:
		file_path = shortcuts[shortcut]
	except KeyError:
		return f"Ярлык {shortcut} не найден."

	try:
		subprocess.run([file_path], check=True)
		file_path = file_path.split("\\")[-1:]
		return f"Ярлык {shortcut} Запущен."
	except subprocess.CalledProcessError as e:
		return f"Ошибка при запуске файла: {e}"

def split_output(output) -> list:
	msg = []
	if output:
		if len(output) > 4096:
			while len(output) > 0:
				msg.append(output[:4096])
				output = output[4096:]
	else:
		msg.append("Вывод консоли пуст.")
	return msg

def check_pid(pid, processes) -> tuple:
	try:
		pid = int(pid)
	except ValueError:
		return ("Пожалуйста, укажите PID процесса.", False)
	if len(processes) == 0:
		return ("Сначала пропишите /processes.", False)
	try:
		proc_name = processes[pid]
	except KeyError:
		return ("Процесс не найден.", False)
	return (proc_name, True)
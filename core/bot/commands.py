import os
import json
import signal
import time
import pythoncom
import wave
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

import psutil
import pyautogui
import telebot
import pyaudio
import numpy
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

from .. import utils
from ..logger import logger

class Commands:
    def __init__(self, bot: telebot.TeleBot, shortcuts: dict) -> None:
        self.processes = {}
        self.wait_off = False
        self.current_dir = ""
        self.shortcuts = shortcuts
        self.recording = False

        self.bot = bot
        self.cmd_dict = {
            "/sleep": self.handle_sleep,
            "/lock": self.handle_lock,
            "/status": lambda message: self.bot.send_message(message.chat.id, "ПК <b>включен</b>."),
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
            "/processes": self.handle_processes,
            "/removepath": self.handle_removepath,
            "/setvolume": self.handle_setvolume,
            "/record": self.handle_record
        }

    def removepath_callback(self, call: telebot.types.CallbackQuery):
        shortcut = call.data[11:]
        try:
            self.shortcuts[shortcut]
            self.shortcuts.pop(shortcut)
            with open("config/shortcuts.json", mode="w") as f:
                json.dump(self.shortcuts, f, indent=4)
            msg = f"Ярлык <code>{shortcut}</code> удалён."
        except KeyError:
            msg = "<i>Ярлык не найден.</i>"
        self.bot.send_message(call.from_user.id, msg)

    def fastrun_callback(self, call: telebot.types.CallbackQuery):
        msg = utils.run_shortcut(call.data[8:], self.shortcuts)
        self.bot.send_message(call.from_user.id, msg)
    
    def handle_screenshot(self, message: telebot.types.Message):
        screen = pyautogui.screenshot(allScreens=True)
        if not os.path.isdir("temp"):
            os.mkdir("temp")
        path = f"temp/screen_{utils.generate_random_string()}.png"
        screen.save(path)
        with open(path, "rb") as photo:
            self.bot.send_document(message.chat.id, photo, reply_to_message_id=message.id)
        os.remove(path)

    def handle_sleep(self, message: telebot.types.Message):
        self.bot.send_message(message.chat.id, "Перевожу ПК в <b>режим сна</b>...")
        os.system("Rundll32.exe powrprof.dll,SetSuspendState Sleep")
    
    def handle_lock(self, message: telebot.types.Message):
        os.system("Rundll32.exe user32.dll,LockWorkStation")
        self.bot.send_message(message.chat.id, "ПК <b>заблокирован</b>.")
    
    def handle_workload(self, message: telebot.types.Message):
        cpu_percent = psutil.cpu_percent()
        while cpu_percent == 0:
            cpu_percent = psutil.cpu_percent()
            time.sleep(0.1)
        ram_percent = psutil.virtual_memory().percent
        ram_total = round(psutil.virtual_memory().total / (1024 **3))
        ram_used = round(psutil.virtual_memory().used / (1024 **3), 1)
        self.bot.send_message(message.chat.id, f"""Загруженность ПК:
<b>CPU:</b> <code>{cpu_percent}%</code>
<b>RAM:</b> <code>{ram_used}GB/{ram_total}GB</code> (<code>{ram_percent}%</code>)
""")
    
    def handle_shutdown(self, message: telebot.types.Message):
        msg = "<b>Выключаю</b> ПК..."
        msg_split = message.text.split(" ")
        t = utils.arg_to_time(msg_split)
        if t > 0:
            msg = f"ПК <b>выключится</b> через <b>{t}</b> секунд...\nВы можете <b>отменить выполнение команды</b>, используя /waitbreak"
        self.bot.send_message(message.chat.id, msg)
        self.wait_off = True
        os.system(f"shutdown /s /t {t}")
    
    def handle_cmd(self, message: telebot.types.Message):
        command = message.text[5:]
        if command:
            try:
                if self.current_dir:
                    os.chdir(self.current_dir)
                output = os.popen(command).read().encode("cp1251").decode("cp866")
                print(output)
                msgs = utils.split_output(output)
                for msg in msgs:
                    self.bot.send_message(message.chat.id, msg)
                return
            except Exception as e:
                msg = f"<b>Ошибка:</b> <code>{str(e)}</code>"
        else:
            msg = "<i>Пожалуйста, укажите команду.</i>"
        self.bot.send_message(message.chat.id, msg)
    
    def handle_cd(self, message: telebot.types.Message):
        path = message.text[4:]
        if path:
            try:
                os.chdir(path)
                self.current_dir = path
                msg = f"Рабочий каталог изменен на: <code>{path}</code>"
            except Exception as e:
                msg = f"<i>Ошибка:</i> <code>{str(e)}</code>"
        else:
            msg = "<i>Пожалуйста, укажите путь.</i>"
        self.bot.send_message(message.chat.id, msg)
    
    def handle_waitbreak(self, message: telebot.types.Message):
        msg = "<i>Перезапуск/выключение ПК</i> <b>отменено</b>."
        if self.wait_off:
            os.system("shutdown /a")
        else:
            msg = "<i>Вы не прописывали команду /shutdown или /reboot.</i>"
        self.bot.send_message(message.chat.id, msg)
    
    def handle_reboot(self, message: telebot.types.Message):
        msg = "<b>Перезапускаю</b> ПК..."
        msg_split = message.text.split(" ")
        t = utils.arg_to_time(msg_split)
        if t > 0:
            msg = f"ПК <b>перезапустится</b> через <b>{t}</b> секунд...\nВы можете <b>отменить выполнение команды</b>, используя /waitbreak"
        self.bot.send_message(message.chat.id, msg)
        self.wait_off = True
        os.system(f"shutdown /g /t {t}")
    
    def handle_runfile(self, message: telebot.types.Message):
        msg = utils.run_file(message.text[9:])
        self.bot.send_message(message.chat.id, msg)
    
    def handle_savepath(self, message: telebot.types.Message):
        msg_split = message.text.split(" ")
        if len(msg_split) <3:
            return self.bot.send_message(message.chat.id, """Пожалуйста, <b>укажите имя ярлыка без пробелов</b> и <b>путь до файла по формату:</b>
<code>/savepath &lt;имя ярлыка&gt; &lt;полный путь&gt;</code>""")
        
        shortcut_name = msg_split[1]
        file_path = " ".join(msg_split[2:])
        self.shortcuts[shortcut_name] = file_path
        with open("config/shortcuts.json", mode="w") as f:
            json.dump(self.shortcuts, f, indent=4)
        msg = f"Ярлык <code>{shortcut_name}</code> сохранён."
        self.bot.send_message(message.chat.id, msg)
    
    def handle_removepath(self, message: telebot.types.Message):
        chat_id = message.chat.id
        shortcut = message.text[12:]
        keyboard = utils.find_shortcuts(self.shortcuts, "removepath")
        if not keyboard:
            return self.bot.send_message(chat_id, "<i>У вас нет ярлыков.</i>")
        if shortcut:
            try:
                self.shortcuts[shortcut]
                self.shortcuts.pop(shortcut)
                with open("config/shortcuts.json", mode="w") as f:
                    json.dump(self.shortcuts, f, indent=4)
                return self.bot.send_message(message.chat.id, f"Ярлык <code>{shortcut}</code> удалён.")
            except KeyError:
                msg = "<i>Ярлык не найден.</i>"
        else:
            msg = "<i>Пожалуйста, укажите имя ярлыка</i>."
        self.bot.send_message(message.chat.id, msg, reply_markup=keyboard)
    
    def handle_fastrun(self, message: telebot.types.Message):
        chat_id = message.chat.id
        shortcut = message.text[9:]
        keyboard = utils.find_shortcuts(self.shortcuts)
        if not keyboard:
            return self.bot.send_message(chat_id, "<i>У вас нет ярлыков.</i>")
        if shortcut:
            msg = utils.run_shortcut(shortcut, self.shortcuts)
            return self.bot.send_message(chat_id, msg)
        self.bot.send_message(chat_id, "<i>Пожалуйста, укажите имя ярлыка.</i>", reply_markup=keyboard)
        
    def handle_kill(self, message: telebot.types.Message):
        pid = message.text[6:]
        data, result = utils.check_pid(pid, self.processes)
        if result:
            pid = int(pid)
            os.kill(pid, signal.SIGTERM)
            self.processes = {}
            msg = f"Процесс <i>{data}</i> завершён.\nПропишите /processes чтобы <b>проверить выполнение</b> команды или <b>отключить другой процесс</b>."
        else:
            msg = data
        self.bot.send_message(message.chat.id, msg)

    def handle_processes(self, message: telebot.types.Message):
        msg = """Чтобы <b>завершить процесс</b> напишите: <code>/kill &lt;pid&gt;</code>
Пример: <code>/kill 3301</code>

<i>Активные процессы:</i>
"""
        self.processes = {}
        for p in psutil.process_iter():
            name = p.name()
            pid = p.pid
            if utils.check_proccess(name, self.processes):
                msg += f"\n<b>{name}</b> <i>(pid: </i><code>{pid}</code><i>) (Статус: {p.status()})</i>"
                self.processes[pid] = name
        msgs = utils.split_output(msg)
        for msg_ in msgs:
            self.bot.send_message(message.chat.id, msg_)
    
    def handle_setvolume(self, message: telebot.types.Message):
        volume = message.text[11:]
        try:
            volume = round(int(volume))
        except ValueError:
            volume = 0
        volume = round((min(100, max(0, volume)) / 100.0), 2)

        pythoncom.CoInitialize()

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume_ = cast(interface, POINTER(IAudioEndpointVolume))
        old_volume = volume_.GetMasterVolumeLevelScalar()
        volume_.SetMasterVolumeLevelScalar(volume, None)

        self.bot.send_message(message.chat.id, f"<b>Общая громкость</b> установлена с <b>{round(old_volume*100)}%</b> на <b>{round(volume*100)}%</b>.")
    
    def handle_record(self, message: telebot.types.Message):
        if self.recording:
            return self.bot.send_message(message.chat.id, "<i>Дождитесь окончания предыдущей записи.</i>")
        
        t = utils.arg_to_time(message.text.split(" "))
        t = min(300, max(0, t))
        t = 30 if t==0 else t

        chunk = 1024
        fmt = pyaudio.paInt16
        rate = 44100
        frames = []
        p = pyaudio.PyAudio()

        stream = p.open(
            format=fmt,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=chunk
        )

        logger.log("Start recording...", 0)
        self.recording = True
        self.bot.send_message(message.chat.id, f"Установлено время записи: <b>{t}</b> сек.\nНачало записи...")

        for _ in range(0, int(rate / chunk * t)):
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        
        for i in range(len(frames)):
            chunk = numpy.fromstring(frames[i], numpy.int16)
            chunk = chunk * 3.0
            frames[i] = chunk.astype(numpy.int16)

        if not os.path.isdir("temp"):
            os.mkdir("temp")
        output_file = f"temp/record_{utils.generate_random_string()}.wav"
        with wave.open(output_file, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(p.get_sample_size(fmt))
            wf.setframerate(rate)
            wf.writeframes(b"".join(frames))

        logger.log("Done recording.", 0)
        self.recording = False
        with open(output_file, "rb") as audio:
            self.bot.send_voice(message.chat.id, audio, reply_to_message_id=message.id)
        os.remove(output_file)
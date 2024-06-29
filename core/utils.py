import json
import os
import sys
import random
import string

import telebot

from .logger import logger

def get_username(message: telebot.types.Message) -> str:
    user = message.from_user
    if user.username:
        return user.username
    if user.first_name:
        return f"{user.first_name} {user.last_name or ''}".strip()
    return user.last_name or "Noname"

def is_exe() -> bool:
    return getattr(sys, 'frozen', False)

def get_resource_path(resource_name: str) -> str:
    if is_exe():
        base_path = sys._MEIPASS
        resource_name = resource_name.replace("core/", "")
    else:
        base_path = os.path.dirname(os.path.dirname(__file__))
    
    return os.path.join(base_path, resource_name)

def generate_random_string(length: int=6) -> str:
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))

def arg_to_time(splitted: list) -> int:
    t = 0
    if len(splitted) > 1:
        try:
            t = round(int(splitted[1]))
            if t < 1:
                t = 0
        except ValueError:
            t = 0
    return t

def find_shortcuts(shortcuts: dict, data: str="fastrun") -> telebot.types.InlineKeyboardMarkup | None:
    if not shortcuts:
        return None
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for shortcut in shortcuts.keys():
        btn = telebot.types.InlineKeyboardButton(f"{shortcut}", callback_data=f"{data}_{shortcut}")
        keyboard.add(btn)
    return keyboard

def load_config(check: bool=True) -> tuple | dict:
    if not os.path.isdir("config"):
        os.mkdir("config")
    path = "config/config.json"
    default_config = {"token": "", "uid": 0, "password": "", "max_users": 2, "users": {}, "autorun": False, "bot_autorun": False}

    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = default_config
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        if check:
            logger.log("config.json is empty.", 3)
            return {}, False
        else:
            return data
    
    for key in default_config.keys():
        data.setdefault(key, default_config[key])
        if key == "token" and check and not data[key]:
            logger.log("token not found in config.", 3)
            return ({}, False)
    return (data, True) if check else data

def load_json(path) -> dict:
    logger.log(f"Loading {path}...", 0)
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def save_json(path: str, data: dict) -> None:
    dir_ = os.path.dirname(path)
    if not os.path.isdir(dir_):
        os.mkdir(dir_)
    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def run_file(path: str=None) -> str:
    if path:
        try:
            os.startfile(path)
            return f"Файл <code>{os.path.basename(path)}</code> Запущен."
        except Exception as e:
            return f"<i>Ошибка при запуске файла:</i> <code>{e}</code>"
    else:
        return "<i>Пожалуйста, укажите путь до файла</i>."

def run_shortcut(shortcut: str, shortcuts: dict) -> str:
    path = shortcuts.get(shortcut)
    if not path:
        return f"Ярлык <code>{shortcut}</code> не найден."

    try:
        os.startfile(path)
        return f"Ярлык <code>{shortcut}</code> <code>({os.path.basename(path)})</code> Запущен."
    except Exception as e:
        return f"<i>Ошибка при запуске файла:</i> <code>{e}</code>"

def split_output(output: str) -> list:
    msg = []
    while output:
        msg.append(output[:4096])
        output = output[4096:]
    return msg if msg else ["<i>Вывод консоли пуст.</i>"]

def check_pid(pid: str, processes: dict) -> tuple:
    try:
        pid = int(pid)
    except ValueError:
        return "<i>Пожалуйста, укажите <b>PID</b> процесса.</i>", False
    
    if not processes:
        return "<i>Сначала пропишите /processes.</i>", False
    
    proc_name = processes.get(pid)
    if not proc_name:
        return "<i>Процесс не найден.</i>", False
    
    return proc_name, True

def check_proccess(name: str, processes: dict) -> bool:
    ignore_list = ["System Idle Process", "System", "Registry", "smss.exe", "lsass.exe", "csrss.exe", "fontdrvhost.exe", "wininit.exe", "services.exe",
             "TextInputHost.exe", "RuntimeBroker.exe", "MemCompression", "spoolsv.exe", "mDNSResponder.exe", "WXCastService.exe", "MsMpEng.exe",
             "SearchIndexer.exe", "dwm.exe", "taskhostw.exe", "dllhost.exe", "conhost.exe", "AggregatorHost.exe", "SgrmBroker.exe", "ShellExperienceHost.exe",
             "winlogon.exe", "CompPkgSrv.exe", "powershell.exe", "nvsphelper64.exe", "NisSrv.exe", "UserOOBEBroker.exe", "StartMenuExperienceHost.exe",
             "SystemSettings.exe", "audiodg.exe", "LockApp.exe", "CalculatorApp.exe", "SearchProtocolHost.exe", "sihost.exe", "SearchApp.exe", "explorer.exe",
             "SearchFilterHost.exe", "ApplicationFrameHost.exe", "smartscreen.exe", "svchost.exe", "WmiPrvSE.exe", "PhoneExperienceHost.exe", "TiWorker.exe",
             "TrustedInstaller.exe", "MoUsoCoreWorker.exe", "WMIRegistrationService.exe", "IntelCpHDCPSvc.exe", "IntelCpHeciSvc.exe", "igfxEM.exe", "igfxCUIService.exe",
             "NVDisplay.Container.exe", "amdfendrsr.exe", "atiesrxx.exe", "msedge.exe", "ctfmon.exe", "atieclxx.exe", "AMDRSServ.exe", "OneApp.IGCC.WinService.exe",
             "MpDefenderCoreService.exe", "jhi_service.exe", "gamingservicesnet.exe", "gamingservices.exe", "Video.UI.exe", "AMDRSSrcExt.exe", "MpCmdRun.exe",
             "SecurityHealthSystray.exe", "SecurityHealthService.exe", "HxOutlook.exe", "AppleMobileDeviceProcess.exe", "RadeonSoftware.exe", "Microsoft.Msn.Weather.exe",
             "HxTsr.exe", "cncmd.exe", "amdow.exe", "nvcontainer.exe", "WUDFHost.exe", "WpcMon.exe", "unsecapp.exe", "AppleMobileDeviceService.exe",
             "AdminService.exe", "CxAudioSvc.exe", "CxAudMsg64.exe", "CxUIUSvc32.exe", "CxUtilSvc.exe", "OfficeClickToRun.exe", "avp.exe", "ICEsoundService64.exe",
             "QcomWlanSrvx64.exe", "dasHost.exe", "rundll32.exe", "avpui.exe", "CPUMetricsServer.exe", "SmartAudio.exe"]
    starts_with_list = ["asus", "nvidia", "lghub"]
    
    if name not in ignore_list and name not in processes.values():
        for prefix in starts_with_list:
            if (name.lower()).startswith(prefix):
                return False
        return True
    return False
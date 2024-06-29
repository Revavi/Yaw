import getpass
import os
import sys
import pythoncom

import flet
from win32com.client import Dispatch

from .. import utils

class Settings:
    def __init__(self, page: flet.Page) -> None:
        self.page = page
        self.theme = self.page.page_theme
        self.config = utils.load_config(False)

        self.bs = self.build()
        self.page.overlay.append(self.bs)
    
    def build(self) -> flet.BottomSheet:
        btn_style = self.get_style()
        text_style = flet.TextStyle(color=self.theme["sidebar_text"], font_family="Default")
        border_style = {
            "border_color": self.theme["sidebar_text"],
            "border_radius": 8,
            "border_width": 2,
            "content_padding": 9
        }
        self.token = flet.TextField(
            label="Токен бота",
            height=40,
            width=1480,
            password=True,
            can_reveal_password=True,
            value=self.config["token"],
            on_change=self.edit_token,
            text_style=text_style,
            label_style=text_style,
            **border_style
        )
        self.uid = flet.TextField(
            label="Ваш UID",
            height=40,
            width=277,
            input_filter=flet.InputFilter(
                allow=True, regex_string=r"[0-9]", replacement_string=""
            ),
            value=self.config["uid"],
            on_change=self.edit_uid,
            text_style=text_style,
            label_style=text_style,
            **border_style
        )
        self.autorun = flet.Switch(
            label="Авто-запуск",
            value=str(self.config["autorun"]),
            height=40,
            on_change=self.edit_autorun
        )
        self.autorun_bot = flet.Switch(
            label="Авто-запуск бота",
            value=str(self.config["bot_autorun"]),
            height=40,
            on_change=self.edit_botautorun
        )

        text = flet.Text("Настройки", size=20, font_family="Bold", color=self.theme["main_text"])
        close = flet.IconButton(
            flet.icons.CLOSE, on_click=self.turn_show, style=btn_style, icon_size=20, height=28, width=28
        )
        return flet.BottomSheet(
            flet.Container(
                content=flet.Column(
                    controls=[
                        flet.Row([text, close], alignment=flet.MainAxisAlignment.SPACE_BETWEEN),
                        self.token,
                        flet.Row([self.uid, self.autorun, self.autorun_bot], width=1500)
                    ],
                    tight=True,
                    expand=True
                ),
                padding=10,
                border_radius=8,
                bgcolor=self.theme["main_bg"],
                expand=True
            ),
            bgcolor=self.theme["main_bg"]
        )

    def get_style(self) -> flet.ButtonStyle:
        return flet.ButtonStyle(
            color=self.theme["main_text"],
            shape=flet.RoundedRectangleBorder(radius=8),
            bgcolor=self.theme["sidebar_bg"],
            padding=0
        )

    def turn_show(self, _=None):
        self.bs.open = not self.bs.open
        self.page.update()
    
    def edit_config(self, key: str, data: any) -> None:
        self.config[key] = data
        utils.save_json("config/config.json", self.config)
    
    def edit_token(self, e: flet.ControlEvent):
        self.edit_config("token", e.data)
    
    def edit_uid(self, e: flet.ControlEvent):
        self.edit_config("uid", int(e.data))
    
    def edit_autorun(self, e: flet.ControlEvent):
        data = e.data == "true"
        user_name = getpass.getuser()
        path = rf"C:\Users\{user_name}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Yaw.lnk"
        if utils.is_exe():
            target = sys.executable
        else:
            target = utils.get_resource_path("main.py")
            if not os.path.isfile(target):
                target += "w"
        
        if data:
            pythoncom.CoInitialize()
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.save()
        else:
            if os.path.exists(path):
                os.remove(path)
        self.edit_config("autorun", data)
    
    def edit_botautorun(self, e: flet.ControlEvent):
        self.edit_config("bot_autorun", True if e.data == "true" else False)
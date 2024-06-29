import sys

import flet
import pystray
from PIL import Image

from ..bot.main import manager
from .. import utils

class AppBar:
    def __init__(self, page: flet.Page) -> None:
        self.page: flet.Page = page
        self.theme = page.page_theme

        tray_image = Image.open(utils.get_resource_path("core/interface/img/icon.ico"))
        self.tray_icon = pystray.Icon(
            name="Yaw",
            icon=tray_image,
            title="Yaw",
            menu=pystray.Menu(
                pystray.MenuItem("Yaw", self.name, enabled=False, default=True),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Открыть", self.open_app),
                pystray.MenuItem("Выход",self.exit_app)
            )
        )
        self.tray_icon.run_detached(setup=self.tray_setup)

        self.appbar_ = self.build()
    
    def build(self) -> flet.Container:
        color = self.theme["title_text"]
        bg = self.theme["title_bg"]
        hovered = self.theme["title_btn_bg_hovered"]

        title = flet.Row(
            [
                flet.Text(""),
                flet.Image(utils.get_resource_path("core/interface/img/logo.svg"), fit=flet.ImageFit.CONTAIN, height=25, width=25),
                flet.Text(self.page.title, size=16, font_family="Bold", color=color)
            ], spacing=4
        )

        self.buttons = flet.Row([
            flet.IconButton(
                flet.icons.MAXIMIZE_ROUNDED, icon_size=22, height=32, width=40, on_click=self.minimize,
                style=self.title_btn_style(hovered, flet.padding.only(top=12.5))
            ),
            flet.IconButton(
                flet.icons.FULLSCREEN_ROUNDED, icon_size=22, height=32, width=40, on_click=self.maximize,
                style=self.title_btn_style(hovered)
            ),
            flet.IconButton(
                flet.icons.CLOSE, icon_size=22, height=32, width=40, on_click=self.close,
                style=self.title_btn_style()
            )], spacing=0)

        return flet.Container(
            flet.WindowDragArea(
                flet.Row([title, self.buttons], alignment=flet.MainAxisAlignment.SPACE_BETWEEN),
                expand=True
            ),
            bgcolor=bg,
            height=32
        )
    
    def title_btn_style(self, hover_bg: str = "#df0000", padding: flet.Padding = flet.padding.all(0)) -> flet.ButtonStyle:
        color_dict = {flet.MaterialState.DEFAULT: self.theme["title_text"], flet.MaterialState.HOVERED: self.theme["title_text_hovered"]}
        bg_dict = {flet.MaterialState.HOVERED: hover_bg}
        return flet.ButtonStyle(
            color=color_dict,
            bgcolor=bg_dict,
            padding={flet.MaterialState.DEFAULT: padding},
            shape={flet.MaterialState.DEFAULT: flet.RoundedRectangleBorder(radius=0)}
        )
    
    def minimize(self, e: flet.ControlEvent):
        self.page.window_minimized = True
        self.page.update()
    
    def maximize(self, e: flet.ControlEvent):
        self.page.window_maximized = not self.page.window_maximized
        self.page.update()
    
    def fullscreen_icon(self, e: flet.ControlEvent):
        if e.data == "maximize":
            self.buttons.controls[1].icon = flet.icons.FULLSCREEN_EXIT_ROUNDED
        elif e.data == "unmaximize":
            self.buttons.controls[1].icon = flet.icons.FULLSCREEN_ROUNDED
    
    def open_app(self, icon, query):
        self.page.window.visible = True
        self.page.update()
    
    def exit_app(self, icon, query):
        if manager.get_status():
            manager.stop()
        self.page.window_destroy()
        icon.stop()
        sys.exit(0)
    
    def tray_setup(self, icon):
        icon.visible = True
    
    def close(self, e: flet.ControlEvent):
        self.page.window.visible = False
        self.page.update()
    
    def name(self, _, __): # for name in tray
        pass
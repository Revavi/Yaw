import flet

from .appbar import AppBar
from .sidebar import Sidebar
from .settings import Settings
from .. import utils
from ..logger import logger

class GUI:
    def __init__(self, page: flet.Page) -> None:
        self.page = page
        self.theme = {
            "title_text": "#878e9c",
            "title_text_hovered": "#ffffff",
            "title_bg": "#21252b",
            "title_btn_bg_hovered": "#3f4247",
            "main_bg": "#282c34",
            "main_text": "#ffffff",
            "sidebar_bg": "#21252b",
            "sidebar_btn_bg": "#2c3139",
            "sidebar_btn_dbg": "#262b32",
            "sidebar_text": "#d5d7e0",
            "sidebar_dtext": "#81848d",
        }
        self.page.page_theme = self.theme
    
        self.build_page()
    
    def build_page(self) -> None:
        self.page.padding = 0
        self.page.window_width, self.page.window_height = 1184, 665 # default size (1168x657) (16:9) (+16 +8)
        self.page.window_min_width, self.page.window_min_height = 616, 658 # min size (600x650) (12:13) (+16 +8)
        self.page.title = "Yaw"
        self.page.window_title_bar_hidden = True
        self.page.fonts = {"Default": "SegoeUI.ttf", "Bold": "SegoeUI-Bold.ttf"}
        self.page.bgcolor = self.theme["main_bg"]

        self.page.on_window_event = self.on_window_event

        self.settings = Settings(self.page)
        self.page.show_setts = self.settings.turn_show

        self.appbar_class = AppBar(self.page)
        self.sidebar_class = Sidebar(self.page)
        self.logzone = flet.Container(
            flet.Column(
                controls=[
                    flet.Text(
                        color=self.theme["main_text"],
                        size=10,
                        selectable=True
                    )
                ],
                expand=True,
                width=10000,
                scroll=flet.ScrollMode.HIDDEN
            ),
            alignment=flet.alignment.top_left,
            expand=True,
            padding=8
        )
        
        logger.subscribe(self.update_logzone)

        self.page.add(
            flet.Column(
                [
                    self.appbar_class.appbar_,
                    flet.Row(
                        [self.sidebar_class.sidebar_, self.logzone], expand=True, spacing=0
                    )
                ], expand=True, spacing=0
            )
        )
        
        config = utils.load_config(False)
        if config["bot_autorun"] == True:
            self.sidebar_class.init_bot()
    
    def update_logzone(self) -> None:
        self.logzone.content.controls[0].value = "\n".join(logger.get_logs())
        self.page.update()
    
    def on_window_event(self, e: flet.ControlEvent):
        if e.data in ["maximize", "unmaximize"]:
            self.appbar_class.fullscreen_icon(e)
            self.page.update()

def run():
    flet.app(target=GUI, assets_dir=utils.get_resource_path("core/interface/fonts"))
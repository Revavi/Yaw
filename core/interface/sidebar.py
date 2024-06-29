import flet

from .. import utils
from ..bot.main import YawBot, manager
from ..logger import logger

class Sidebar:
    def __init__(self, page: flet.Page) -> None:
        self.page = page
        self.theme = page.page_theme

        self.info = self.build_info()
        self.sidebar_ = self.build()
    
    def build(self) -> flet.Container:
        btn_style = self.get_style()
        buttons = [
            {"label": "Запуск бота", "func": self.init_bot},
            {"label": "Остановка бота", "func": self.stop_bot},
            {"label": "Очистить логи", "func": logger.clear_logs},
            {"label": "Настройки", "func": self.settings}
        ]
        
        items = [
            flet.TextButton(
                text=button["label"],
                style=btn_style,
                width=190,
                on_click=button["func"]
            ) for button in buttons
        ]
        items[1].disabled = True
        items = flet.Column(items, expand=True)

        sidebar = [
                items,
                flet.Row(
                    [
                        flet.IconButton(
                            flet.icons.INFO_OUTLINED,
                            icon_color=self.theme["sidebar_text"],
                            icon_size=30,
                            on_click=self.showinfo,
                            style=flet.ButtonStyle(bgcolor={flet.MaterialState.HOVERED: self.theme["sidebar_btn_bg"]})
                        )
                    ], alignment=flet.MainAxisAlignment.CENTER)
            ]

        return flet.Container(
            content=flet.Column(sidebar, tight=True),
            padding=4,
            margin=0,
            width=200,
            bgcolor=self.theme["sidebar_bg"]
        )

    def build_info(self) -> flet.AlertDialog:
        info = """# Вы используете версию **2.0**
[Github репозиторий проекта](https://github.com/Revavi/Yaw)

## **Разработчики**
 - [**Revavi**](https://t.me/CleanVeins) - *Основной кодер*
 - [**msihek**](https://github.com/msihek) - *помощь в разработке, автор некоторых идей*
 - [**Chonnon**](https://t.me/wtflony) - *Автор некоторых идей, помощь с созданием лого, бета-тестер*

## Для работы программы вы **должны**:
  1. создать **телеграмм бота** через [BotFather](https://t.me/BotFather) или взять существующего,
а затем поместить его токен в поле **Токен бота** в настройках. **Никто, кроме вас, не должен знать токен бота!**
  2. Получить **ваш UID** и поместить его в поле **Главный UID** в настройках.
Его можно получить при запуске бота и использовании **любой** команды, или же через [userinfobot](https://t.me/userinfobot).
"""
        return flet.AlertDialog(
            modal=True,
            title=flet.Text("Yaw", size=35, font_family="Bold"),
            content=flet.Markdown(info, extension_set=flet.MarkdownExtensionSet.GITHUB_WEB,
                                  on_tap_link=lambda e: self.page.launch_url(e.data)),
            actions=[flet.TextButton("Закрыть", on_click=self.closeinfo)],
            actions_alignment=flet.MainAxisAlignment.END,
            bgcolor=self.theme["main_bg"]
        )

    def get_style(self) -> flet.ButtonStyle:
        return flet.ButtonStyle(
            color={
                flet.MaterialState.DEFAULT: self.theme["sidebar_text"],
                flet.MaterialState.DISABLED: self.theme["sidebar_dtext"]
            },
            shape=flet.RoundedRectangleBorder(radius=8),
            bgcolor={
                flet.MaterialState.DEFAULT: self.theme["sidebar_btn_bg"],
                flet.MaterialState.DISABLED: self.theme["sidebar_btn_dbg"]
            }
        )

    def showinfo(self, e: flet.ControlEvent):
        self.page.dialog = self.info
        self.info.open = True
        self.page.update()
    
    def closeinfo(self, e: flet.ControlEvent):
        self.info.open = False
        self.page.update()
    
    def block_turn(self, start: bool=True, stop: bool=False) -> None:
        self.sidebar_.content.controls[0].controls[0].disabled = start
        self.sidebar_.content.controls[0].controls[1].disabled = stop
        self.page.update()

    def init_bot(self, e: flet.ControlEvent=None):
        config, result = utils.load_config()

        if result:
            self.block_turn()
            manager.add_func(self.block_turn)
            manager.init_bot(YawBot(config))
            manager.run()
    
    def settings(self, e: flet.ControlEvent):
        self.page.show_setts()
    
    def stop_bot(self, e: flet.ControlEvent):
        self.block_turn(True, True)
        manager.stop()
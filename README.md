# PCRCB (V 1.1)
P_ersonal_C_omputer_R_emote_C_ontrol_B_ot_

Персональный телеграм бот для управления компьютером на растоянии.

_Авторы: Revavi (Основной кодер), msihek(Помощь в разработке)_

## Команды бота

**/status** - *проверяет статус ПК (Вкл/выкл)*
**/shutdown** - *полностью выключает ПК и бота*
**/lock** - *блокирует ПК без выключения*
**/sleep** - *вводит ПК в режим сна*
**/reboot** - *перезапуск ПК*
**/screenshot** - *делает скриншот монитора*
**/workload** - *выводит данные загруженности процессора и оперативной памяти ПК*
**/processes** - *выводит список запущенных процессов на ПК*
**/kill <PID>** - *убивает процесс по его ID на ПК*
**/runfile <полный путь до файла>** - *запускает файл на ПК по указанному пути*
**/savepath <имя ярлыка без пробелов> <полный путь до файла>** - *сохраняет ярлык для быстрого запуска файла на ПК*
**/fastrun <имя ярлыка>** - *запускает файл по сохранённому ранее ярлыку*

## Скриншоты/Видео

*Появятся после релиза v1.3*

## Зависимости

  - **Python**
  - **telebot (pip install pyTelegramBotAPI)**
  - **PyAutoGui (pip install PyAutoGUI)**
  - **PSUtil (pip install psutil)**

  _Код писался на версиях:_
  - **Python v3.11.8**
  - **telebot v4.18.1**
  - **PyAutoGui v0.9.54**
  - **PSUtil v5.9.8**

## Как установить

  1. Скачайте последнюю версию бота в релизах, затем разархивируйте все файлы в одну папку.
  2. В файле config.json пропишите токен заранее созданного телеграмм бота и ваш UID, который вы можете получить при запуске бота и прописывании любой команды.
  3. Запустите исходный код (main.py) или исполняемый файл pcrcb.exe.

## Связь с разработчиком

**Discord: _revavi_**  
[**telegram**](https://t.me/CleanVeins)
[**VK**](https://vk.com/revavi)

## Список изменений
***Подробнее вы можете узнать в информации про релизы***

**V 1.0 (Полностью написанна Revavi) >>**
  - /shutdown

**V 1.1 (Полностью написанна msihek) >>**
  - /sleep
  - /reboot
  - Изменение кода, названия команд
 
**V 1.2 >>**
  - /lock
  - /status
  - /screenshot
  - /workload
  - /processes
  - /runfile
  - /savepath
  - /fastrun
  - Изменение кода, названия команд

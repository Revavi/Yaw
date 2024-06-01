# PCRCB (V 1.3)
**P***ersonal* **C***omputer* **R***emote* **C***ontrol* **B***ot*

Персональный телеграм бот для управления компьютером на растоянии.

_Авторы: **Revavi** (Основной кодер), **msihek** (Помощь в разработке)_

## Команды бота

**/status** - *проверяет статус ПК (Вкл/выкл)*  
**/shutdown <время, сек>** - *полностью выключает ПК и бота через указанный промежуток времени*  
**/lock** - *блокирует ПК без выключения*  
**/sleep** - *вводит ПК в режим сна*  
**/reboot <время, сек>** - *перезапускает ПК через указанный промежуток времени*  
**/screenshot** - *делает скриншот монитора*  
**/workload** - *выводит данные загруженности процессора и оперативной памяти ПК*  
**/processes** - *выводит список запущенных процессов на ПК*  
**/kill <PID>** - *убивает процесс по его ID на ПК*  
**/runfile <полный путь до файла>** - *запускает файл на ПК по указанному пути*  
**/savepath <имя ярлыка без пробелов> <полный путь до файла>** - *сохраняет ярлык для быстрого запуска файла на ПК*  
**/fastrun <имя ярлыка>** - *запускает файл по сохранённому ранее ярлыку*  
**/waitbreak** - *отменяет выключение/перезапуск ПК*
**/cmd <команда>** - *выполняет указанную команду в консоли на ПК*
**/cd <путь>** - *Меняет рабочий каталог для команд /cmd*

## В разработке:

  - Код доверия, для передачи доступа к боту на другие телеграмм аккаунты
  - И многое другое...

## Зависимости

_Позже добавлю список версий, с которыми бот будет работать_

  - **Python**
  - **telebot (pip install pyTelegramBotAPI)**
  - **PyAutoGui (pip install PyAutoGUI)**
  - **PSUtil (pip install psutil)**

  _Код писался на версиях:_
  - **Python v3.11.8**
  - **telebot v4.18.1**
  - **PyAutoGui v0.9.54**
  - **PSUtil v5.9.8**

## Как установить (V1.2+)

  В начале создайте бота через [BotFather](https://t.me/BotFather), используя команду /newbot!  
  Ваш UID вы можете получить при запуска бота и вводе любой команды или же через [этого бота](https://t.me/userinfobot)

  1. Скачайте последнюю версию бота в релизах, затем разархивируйте все файлы в одну папку.
  2. В файле config.json пропишите токен заранее созданного телеграмм бота и ваш UID
  3. Запустите исходный код (main.py) или исполняемый файл pcrcb.exe.

## Связь с разработчиком

**Discord: _revavi_**  
[**telegram**](https://t.me/CleanVeins)  
[**VK**](https://vk.com/revavi)

## Список изменений
***Подробнее вы можете узнать в информации про релизы** (начиная с v1.3)*

**V 1.0 (Полностью написанна Revavi) >>** *НЕ РЕКОМЕНДУЕТСЯ ДЛЯ ИСПОЛЬЗОВАНИЯ*
  - /shutdown

**V 1.1 (Полностью написанна msihek) >>** *НЕ РЕКОМЕНДУЕТСЯ ДЛЯ ИСПОЛЬЗОВАНИЯ*
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

**V 1.3 >>**
  - в разработке...

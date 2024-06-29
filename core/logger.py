import os
from datetime import datetime
from typing import Callable, List

class Logger:
    def __init__(self) -> None:
        self.logs: List[str] = []
        self.subscribers: List[Callable[[], None]] = []

    def log(self, message: str, level: int=1) -> None:
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        level = min(len(levels)-1, max(0, level))
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%y %H:%M:%S.%f")
        msg = f"[{timestamp}][{levels[level]}] >> {message}"
        self.logs.append(msg)
        print(message)
        self.notify_subscribers()
        
        if not os.path.isdir("logs"):
            os.mkdir("logs")
        
        log_filename = now.strftime("%Y_%m_%d.log")
        with open(os.path.join("logs", log_filename), "a", encoding="utf-8") as f:
            f.write(msg + "\n")
    
    def clear_logs(self, _) -> None:
        self.logs = []
        self.notify_subscribers()

    def get_logs(self) -> List[str]:
        return self.logs

    def subscribe(self, callback: Callable[[], None]) -> None:
        self.subscribers.append(callback)

    def notify_subscribers(self) -> None:
        for callback in self.subscribers:
            callback()

logger = Logger()
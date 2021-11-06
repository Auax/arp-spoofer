import datetime
from typing import Any

from colorama import init, Fore, Style

# Colorama autoreset color in new line
init(autoreset=True)


class Logger:
    def __init__(self, save: bool = False):
        self.save = save

    def _log(self, symbol: str, color: Any, text: str):
        print(f"[{color}{symbol}{Style.RESET_ALL}] {color}>>{Style.RESET_ALL} {text}")
        if self.save:
            self._save_log(text)

    def error(self, text):
        self._log("!", Fore.RED, text)

    def warn(self, text):
        self._log("^", Fore.YELLOW, text)

    def info(self, text):
        self._log("~", Fore.WHITE, text)

    def success(self, text):
        self._log("+", Fore.GREEN, text)

    @staticmethod
    def _save_log(text: str):
        with open("output.log", "w") as file:
            file.write(str(datetime.datetime.now()) + " >>> " + text)


L = Logger()
L.error("asdads")

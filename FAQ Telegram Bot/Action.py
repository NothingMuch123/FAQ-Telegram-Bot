from typing import Tuple
from telebot.types import InlineKeyboardMarkup

class Action:
    def __init__(self, name : str) -> None:
        self.Name = name


    # Render the action for display
    def Display(self) -> Tuple[str, InlineKeyboardMarkup]:
        return "", None


    # Render the feedback when selected
    def Selected(self, callback) -> str:
        return ""
from typing import Tuple
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from Action import Action
from QandA import QandA


class Category(Action):
    def __init__(self, name : str, message : str) -> None:
        super().__init__(name)

        # Set up message if not available
        if message == None or len(message) <= 0:
            self.Message = "What do you like to know about " + name + "?"
        else:
            self.Message = message
        self.ActionList = []

        # Set up current selected action as none
        self.SelectedAction = None


    def DisplayMessage(self):
        return self.Message, self.GenerateKeyboardMarkup()


    # Render the feedback when selected
    def Selected(self, callback):

        # If action selected, proceed further into hierarchy
        if self.SelectedAction:
            return self.SelectedAction.Selected(callback)

        # Loop through list of actions
        for a in self.ActionList:
            # Found action that matches callback
            if a.DisplayName() == callback:
                # Check action type
                if type(a) is Category:
                    self.SelectedAction = a
                    return a.DisplayMessage()
                elif type(a) is QandA:
                    self.SelectedAction = None
                    return a.Selected(callback), self.GenerateKeyboardMarkup()

        return self.Message, self.GenerateKeyboardMarkup()

    
    def ToString(self, level) -> str:
        pass


    def AddAction(self, a):
        self.ActionList.append(a)


    def GenerateKeyboardMarkup(self) -> InlineKeyboardMarkup:
        k = InlineKeyboardMarkup()

        for a in self.ActionList:
            name = a.DisplayName()
            k.add(InlineKeyboardButton(name, callback_data=name))

        return k
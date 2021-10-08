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
        #self.SelectedAction = None


    def DisplayMessage(self):
        return self.Message, self.GenerateKeyboardMarkup()


    # Render the feedback when selected
    def Selected(self, callback : str, state):
        # If action selected, proceed further into hierarchy
        if len(state) > 0:
            message, markup, newState = self.ActionList[state[0]].Selected(callback, state[1:])
            newState.insert(0, state[0])
            return message, markup, newState

        # Loop through list of actions
        actionCount = 0
        for a in self.ActionList:
            # Found action that matches callback
            if a.DisplayName() == callback:
                # Check action type
                if type(a) is Category:
                    message, markup = a.DisplayMessage()
                    return message, markup, [actionCount]
                elif type(a) is QandA:
                    return a.Selected(callback, None), self.GenerateKeyboardMarkup(), []

            # Next
            actionCount += 1

        return self.Message, self.GenerateKeyboardMarkup(), []

    
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
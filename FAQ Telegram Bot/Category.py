# Telebot imports
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Constant imports
from Constants import KeyboardButton_Back

# Class imports
from Action import Action
from QandA import QandA


class Category(Action):
    def __init__(self, name : str, message : str, skipBack = False) -> None:
        super().__init__(name)

        # Set up message if not available
        if message == None or len(message) <= 0:
            self.Message = "What do you like to know about " + name + "?"
        else:
            self.Message = message
        self.ActionList = []

        self.SkipBack = skipBack


    def DisplayMessage(self):
        return self.Message, self.GenerateKeyboardMarkup()


    # Render the feedback when selected
    def Selected(self, callback : str, state):
        # If action selected, proceed further into hierarchy
        stateLength = len(state)
        if stateLength > 0:
            # Check if back is pressed
            if stateLength == 1 and callback == KeyboardButton_Back:
                return self.Message, self.GenerateKeyboardMarkup(), []
            else:
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

        # Add all actions as keyboard button
        for a in self.ActionList:
            name = a.DisplayName()
            k.add(InlineKeyboardButton(name, callback_data=name))

        # Add back keyboard button
        if not self.SkipBack:
            k.add(InlineKeyboardButton(KeyboardButton_Back, callback_data=KeyboardButton_Back))

        return k
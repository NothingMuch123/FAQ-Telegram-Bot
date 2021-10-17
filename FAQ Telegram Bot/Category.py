# Telebot imports
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# Constant imports
from Constants import CALLBACK_BACK, ScriptLevel, TabSpacing, NewLine

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


    def DisplayMessage(self, textOnly : bool = False):
        if textOnly:
            return self.Message
        return self.Message, self.GenerateKeyboardMarkup()


    # Render the feedback when selected
    def Selected(self, callback : str, state):
        # If action selected, proceed further into hierarchy
        stateLength = len(state)
        if stateLength > 0:
            # Check if back is pressed
            if stateLength == 1 and callback == CALLBACK_BACK:
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
        # Level
        result = ScriptLevel * level + NewLine

        # Open curly braces
        oneLessTabSpace = TabSpacing * (level - 1)
        result += oneLessTabSpace + "{" + NewLine

        # Name
        tabSpace = TabSpacing * level
        result += tabSpace + "\"Name\" : \"" + self.Name + "\"," + NewLine

        # Message
        result += tabSpace + "\"Message\" : \"" + self.Message + "\"" + NewLine

        # Close curly braces
        result += oneLessTabSpace + "}" + NewLine

        # Add all actions
        for a in self.ActionList:
            result += a.ToString(level + 1)

        return result


    def AddAction(self, a):
        self.ActionList.append(a)


    def GenerateKeyboardMarkup(self, numberCallback : bool = False, forceIgnoreBack : bool = False) -> InlineKeyboardMarkup:
        k = InlineKeyboardMarkup()

        # Add all actions as keyboard button
        count = 0
        for a in self.ActionList:
            name = a.DisplayName()
            k.add(InlineKeyboardButton(name, callback_data=name if not numberCallback else str(count)))
            count += 1

        # Add back keyboard button
        if not self.SkipBack and not forceIgnoreBack:
            k.add(InlineKeyboardButton(CALLBACK_BACK, callback_data=CALLBACK_BACK))

        return k
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from Constants import APPSTATE_FAQ, ROLE_DEFAULT, ROLE_LOCKED, MaxLoginAttempts

class BotUser:
    FEEDBACK_SPLIT = "_"

    def __init__(self, id) -> None:
        self.ID = id

        # App states
        self.FAQState = []
        self.AppState = APPSTATE_FAQ

        # Roles
        self.Role = ROLE_DEFAULT
        self.LoginAttempts = 0

        # Feedback
        self.Feedbacks = []

        # Temp Data
        self.TempData = {}

    
    def ResetFAQState(self):
        self.FAQState = []


    def AttemptLoginFail(self) -> None:
        self.LoginAttempts += 1
        if self.LoginAttempts >= MaxLoginAttempts:
            self.Role = ROLE_LOCKED

    
    def WriteFeedback(self, f : str):
        self.Feedbacks.append(f)


    def RemoveFeedback(self, index : str):
        # Remove feedback
        fIndex = int(index)
        if fIndex >= 0 and fIndex < len(self.Feedbacks):
            del self.Feedbacks[fIndex]


    def RetrieveFeedback(self, index : str) -> str:
        # Retrieve feedback
        fIndex = int(index)
        if fIndex >= 0 and fIndex < len(self.Feedbacks):
            return self.Feedbacks[fIndex]

        # No feedback found
        return None


    def AddFeedbacksIntoMarkup(self, markup : InlineKeyboardMarkup):
        count = 1
        strID = str(self.ID)
        for f in self.Feedbacks:
            markup.add(InlineKeyboardButton(
                "Feedback #" + str(count) + " from " + strID,
                callback_data=strID + BotUser.FEEDBACK_SPLIT + str(count - 1)))
            count += 1
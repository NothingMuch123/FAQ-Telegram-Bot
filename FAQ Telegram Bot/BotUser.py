from Constants import APPSTATE_FAQ, ROLE_DEFAULT, ROLE_LOCKED, MaxLoginAttempts

class BotUser:
    def __init__(self, id) -> None:
        self.ID = id
        self.FAQState = []
        self.AppState = APPSTATE_FAQ

        # Roles
        self.Role = ROLE_DEFAULT
        self.LoginAttempts = 0

    
    def ResetFAQState(self):
        self.FAQState = []


    def AttemptLoginFail(self):
        self.LoginAttempts += 1
        if self.LoginAttempts >= MaxLoginAttempts:
            self.Role = ROLE_LOCKED
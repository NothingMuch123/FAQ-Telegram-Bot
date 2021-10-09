from Constants import APPSTATE_FAQ, ROLE_DEFAULT

class User:
    def __init__(self, id) -> None:
        self.ID = id
        self.FAQState = []
        self.AppState = APPSTATE_FAQ
        self.Role = ROLE_DEFAULT
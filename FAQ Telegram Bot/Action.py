class Action:
    def __init__(self, name : str) -> None:
        self.Name = name


    # Render the action for display
    def Display(self) -> str:
        return ""


    # Render the feedback when selected
    def Selected(self, callback) -> str:
        return ""
class Action:
    def __init__(self, name : str) -> None:
        self.Name = name


    # Return the name
    def DisplayName(self) -> str:
        return self.Name


    def DisplayMessage(self):
        pass


    # Render the feedback when selected
    def Selected(self, callback : str, state):
        pass

    
    def ToString(self, level) -> str:
        pass
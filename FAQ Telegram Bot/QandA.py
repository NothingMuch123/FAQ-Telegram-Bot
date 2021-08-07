from Action import Action

class QandA(Action):
    def __init__(self, q : str, a : str) -> None:
        super().__init__(q)

        self.Answer = a


    # Render the action for display
    def Display(self) -> str:
        return self.Name


    # Render the feedback when selected
    def Selected(self, callback) -> str:
        return self.Answer
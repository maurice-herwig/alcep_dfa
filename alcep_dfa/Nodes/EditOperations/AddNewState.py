from .EditOperation import EditOperation


class AddNewState(EditOperation):

    def __init__(self, state: tuple):
        self.state = state

    def get_state(self) -> tuple:
        return self.state

    def __repr__(self):
        return f"Add {self.state} as a new state"

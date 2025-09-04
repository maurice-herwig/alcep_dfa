from .EditOperation import EditOperation


class LeaveInitial(EditOperation):

    def __init__(self, state: tuple):
        self.state = state

    def get_state(self) -> tuple:
        return self.state

    def __repr__(self):
        return f"Leave {self.state} as initial"

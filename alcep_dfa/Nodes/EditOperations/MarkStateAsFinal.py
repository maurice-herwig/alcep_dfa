from .EditOperation import EditOperation


class MarkStateAsFinal(EditOperation):

    def __init__(self, state: tuple):
        self.state = state

    def __repr__(self):
        return f"Mark {self.state} as a final state"

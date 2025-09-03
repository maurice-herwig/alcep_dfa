from .EditOperation import EditOperation


class MarkAsInitial(EditOperation):

    def __init__(self, state: tuple):
        self.state = state

    def __repr__(self):
        return f"mark {self.state} as initial"

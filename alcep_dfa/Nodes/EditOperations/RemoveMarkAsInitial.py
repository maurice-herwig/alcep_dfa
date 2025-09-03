from .EditOperation import EditOperation


class RemoveMarkAsInitial(EditOperation):

    def __init__(self, state: tuple):
        self.state = state

    def __repr__(self):
        return f" remove {self.state} as a initial node"

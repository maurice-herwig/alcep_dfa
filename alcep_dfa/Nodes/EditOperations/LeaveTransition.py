from .EditOperation import EditOperation


class LeaveTransition(EditOperation):

    def __init__(self, source_state: tuple, symbol: str, target_state: tuple):
        self.source_state = source_state
        self.symbol = symbol
        self.target_state = target_state

    def get_transition(self) -> tuple[tuple, str, tuple]:
        return self.source_state, self.symbol, self.target_state

    def __repr__(self):
        return f"Leave the transition ({self.source_state}, '{self.symbol}', {self.target_state}) unchanged"

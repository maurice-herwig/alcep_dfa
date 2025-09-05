class ForestNode:

    def __init__(self):
        self.all_minimal_edits = None
        self.minimal_edits_costs = None

    def get_all_minimal_edits(self):
        if self.all_minimal_edits is None:
            raise Exception("Minimal edits not computed yet.")
        return self.all_minimal_edits

    def get_minimal_edits_costs(self):
        if self.minimal_edits_costs is None:
            raise Exception("Minimal edits costs not computed yet.")
        return self.minimal_edits_costs

    def set_minimal_edits(self, edits, costs):
        self.minimal_edits_costs = costs
        self.all_minimal_edits = edits

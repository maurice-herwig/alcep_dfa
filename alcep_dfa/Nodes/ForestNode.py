class ForestNode:

    def __init__(self):
        self.all_edits = None
        self.minimal_edits_costs = None
        self.number_of_corrections = None

    def get_all_edits(self):
        if self.all_edits is None:
            raise Exception("Minimal edits not computed yet.")
        return self.all_edits

    def get_minimal_edits_costs(self):
        if self.minimal_edits_costs is None:
            raise Exception("Minimal edits costs not computed yet.")
        return self.minimal_edits_costs

    def set_all_edits(self, edits):
        self.all_edits = edits

    def set_minimal_edits_costs(self, costs):
        self.minimal_edits_costs = costs

    def set_number_of_corrections(self, number):
        self.number_of_corrections = number

    def get_number_of_corrections(self):
        return self.number_of_corrections

from tala.model.semantic_object import SemanticObject

DONE = "done"
ABORTED = "aborted"


class Done(SemanticObject):
    def __eq__(self, other):
        return isinstance(other, Done)

    def as_semantic_expression(self):
        return DONE

    def __str__(self):
        return DONE

    def __repr__(self):
        return "Done()"

    def __hash__(self):
        return hash(DONE)


class Aborted(SemanticObject):
    def __init__(self, reason):
        self._reason = reason

    @property
    def reason(self):
        return self._reason

    def __eq__(self, other):
        return isinstance(other, Aborted) and self.reason == other.reason

    def as_semantic_expression(self):
        return f"{ABORTED}({self.reason})"

    def __str__(self):
        return f"{ABORTED}({self.reason})"

    def __repr__(self):
        return f"Aborted({self.reason})"

    def __hash__(self):
        return hash((ABORTED, self.reason))

class RBACPolicy:
    def __init__(self, assignee, assignee_type, role, scope):
        self.assignee_type = assignee_type
        self.scope = scope
        self.role = role
        self.assignee = assignee


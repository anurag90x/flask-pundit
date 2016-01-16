class ApplicationPolicy:
    def __init__(self, user, record):
        self.user = user
        self.record = record
    class Scope:
        def __init__(self, user, scope):
            self.user = user
            self.scope = scope
        def resolve(self):
            pass

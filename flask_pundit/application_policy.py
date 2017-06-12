class ApplicationPolicy:
    '''Base class for all policy'''
    def __init__(self, user, record):
        self.user = user
        self.record = record

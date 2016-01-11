from flask_pundit.application_policy import ApplicationPolicy

class UserPolicy(ApplicationPolicy):
    def __init__(self):
        pass

class PostPolicy(ApplicationPolicy):
    def get(self):
        return False

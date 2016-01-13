from flask_pundit.application_policy import ApplicationPolicy
import models

class UserPolicy(ApplicationPolicy):
    def __init__(self):
        pass

class PostPolicy(ApplicationPolicy):
    def get(self):
        return False

    def index(self):
        return True

    class Scope:
        def resolve(self):
            return [models.Post(id=1), models.Post(id=2)]

from flask_pundit.application_policy import ApplicationPolicy
from tests.models.post import Post

class PostPolicy(ApplicationPolicy):
    def get(self):
        return True

    def index(self):
        return True

    class Scope:
        def resolve(self):
            return [models.Post(id=1), models.Post(id=2)]

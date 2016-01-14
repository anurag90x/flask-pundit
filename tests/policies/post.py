from flask_pundit.application_policy import ApplicationPolicy
from tests.models.post import Post


class PostPolicy(ApplicationPolicy):
    def get(self):
        return True

    def index(self):
        return True

    class Scope:
        def resolve(self):
            return [Post(id=1), Post(id=2)]

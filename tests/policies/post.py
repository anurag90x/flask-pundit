from flask_pundit.application_policy import ApplicationPolicy
from tests.models.post import Post


class PostPolicy(ApplicationPolicy):
    def get(self):
        if self.user.get('role') == 'admin':
            return True
        return False

    def index(self):
        return True

    class Scope:
        def resolve(self):
            return [Post(id=1), Post(id=2)]

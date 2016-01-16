from flask_pundit.application_policy import ApplicationPolicy
from tests.models.post import Post


class PostPolicy(ApplicationPolicy):
    def get(self):
        if self.user.get('role') == 'admin':
            return True
        return False

    class Scope(ApplicationPolicy.Scope):
        def resolve(self):
            if self.user.get('role') == 'admin':
                return [1, 2]
            return [3, 4]

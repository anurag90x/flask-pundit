from flask_pundit.application_policy import ApplicationPolicy


class PostPolicy(ApplicationPolicy):
    def get(self, *args, **kwargs):
        if kwargs.get('thing_id') == 1:
            return False
        return self.user.get('role') == 'admin'

    def create(self):
        return self.user.get('role') == 'admin'

    def scope(self):
        if self.user.get('role') == 'admin':
            return [1, 2]
        return [3, 4]

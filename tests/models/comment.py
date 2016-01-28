from tests.policies.commenting import CommentingPolicy


class Comment:

    __policy_class__ = CommentingPolicy

    def __init__(self, id):
        self.id = id

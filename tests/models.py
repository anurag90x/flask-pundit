from policies import UserPolicy, PostPolicy

class User:
    policy_class = UserPolicy
    def __init__(self):
        pass

class Post:
    policy_class = PostPolicy
    def __init__(self):
        pass


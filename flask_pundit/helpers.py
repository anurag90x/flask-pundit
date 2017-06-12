import re


def dasherized_name(model_name):
    def dasherize(match):
        name = match.group(0)
        if name[-1].isupper():
            return (name[:-1] + '_' + name[-1]).lower()
        return name.lower()

    return re.sub(
        r'[A-Z0-9]*[a-z0-9]*[A-Z0-9]?', dasherize, model_name)

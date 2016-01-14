def import_module(module_path):
    top_module = __import__(module_path)
    modules = module_path.split('.')[1:]
    return _traverse_path_list(top_module, modules)

def _traverse_path_list(root, modules):
    if len(modules) == 0:
        return root
    return _traverse_path_list(getattr(root, modules.pop(0)), modules)

from .state import get_current_config

class WrappedFunction:

    def __init__(self, func):
        self.func = func
        self.arg_paths = []

    def add_arg(self, arg):
        self.arg_paths.append([None, arg])

    def set_section(self, section):
        for i in reversed(range(len(self.arg_paths))):
            current_ns, path = self.arg_paths[i]
            if current_ns is None:
                self.arg_paths[i][0] = section
            else:
                break

    def __call__(self, *args, **kwargs):
        config = get_current_config()
        filled_args = {}
        for ns, path in self.arg_paths:
            if ns is not None:
                path = ns + path
            value = config[path]
            if value is not None:
                filled_args[path[-1]] = value

        filled_args.update(kwargs)

        try:
            return self.func(*args, **filled_args)
        except TypeError as e:
            if 'multiple values for argument' in e.args[0]:
                raise TypeError("""Ambiguity overriding config arguments, use \
named parameter to resolve it""") from None
            else:
                raise e



def param(parameter):
    if isinstance(parameter, str):
        parameter = tuple(parameter.split('.'))

    def wrapper(func):
        if not isinstance(func, WrappedFunction):
            func = WrappedFunction(func)
        func.add_arg(parameter)
        return func
    return wrapper

def section(section):
    if isinstance(section, str):
        section = tuple(section.split('.'))

    def wrapper(func):
        if not isinstance(func, WrappedFunction):
            func = WrappedFunction(func)
        func.set_section(section)
        return func
    return wrapper

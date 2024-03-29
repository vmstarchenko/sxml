import re
import importlib.util
from .options import Option


def clean_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def patch_options(options, kwargs):
    return {
        k: options[v.key] if isinstance(v, Option) else v
        for k, v in kwargs.items()
    }


def wrap_global(func):
    class KeepArgsCls:
        def __init__(self, namespace, **kwargs):
            self.kwargs = kwargs

        def __call__(self, *args, **kwargs):
            kwargs = {**self.kwargs, **kwargs}
            kwargs = patch_options(kwargs.pop('options'), kwargs)
            return func(*args, **kwargs)

    return KeepArgsCls


# https://docs.python.org/3/library/importlib.html#implementing-lazy-imports
def lazy_import(name):
    '''
    TODO: add lazy import

    # method 1
    spec = importlib.util.find_spec(name)
    if spec is None:
        return None

    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module

    # method 2
    try:
        return sys.modules[name]
    except KeyError:
        pass

    spec = importlib.util.find_spec(name)
    module = importlib.util.module_from_spec(spec)
    loader = importlib.util.LazyLoader(spec.loader)
    loader.exec_module(module)
    return module
    '''

    # return importlib.import_module(name)
    import sys
    spec = importlib.util.find_spec(name)
    if spec is None:
        return None

    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module

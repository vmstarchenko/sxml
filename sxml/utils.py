import re
from .options import Option


def clean_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def patch_options(options, kwargs):
    return {
        k: options[v.key] if isinstance(v, Option) else v
        for k, v in kwargs.items()
    }


def wrap_global(func):
    class keep_args_instance:
        def __init__(self, namespace, **kwargs):
            self.kwargs = kwargs

        def __call__(self, *args, **kwargs):
            kwargs = {**self.kwargs, **kwargs}
            kwargs = patch_options(kwargs.pop('options'), kwargs)
            return func(*args, **kwargs)

    return keep_args_instance

import functools
from lxml import etree
import yaml

from .options import Option


# https://github.com/yaml/pyyaml/issues/165
# https://gist.github.com/pypt/94d747fe5180851196eb
class SxmlLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f'duplicated keys not allowed: {key}')
            mapping.append(key)
        return super().construct_mapping(node, deep)


class SxmlDumper(yaml.SafeDumper):
    pass


class SxmlDebugDumper(SxmlDumper):
    def represent_data(self, data):
        if isinstance(data, etree.ElementBase):
            return element_representer(self, data)
        return super().represent_data(data)


Loader = SxmlLoader
Dumper = SxmlDumper
DebugDumper = SxmlDebugDumper


# def option_representer(dumper, data):
#     return dumper.represent_scalar('!Opt', data.key)


def option_constructor(loader, node):
    value = loader.construct_scalar(node)
    return Option(value)


def element_representer(dumper, data):
    return dumper.represent_scalar('!Xml', str(data))


def add_representer(*args):
    Dumper.add_representer(*args)


load = functools.partial(yaml.load, Loader=Loader)
dump = functools.partial(yaml.dump, Dumper=Dumper, width=float('inf'))

Loader.add_constructor('!Opt', option_constructor)

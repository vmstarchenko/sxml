from typing import Any, Union
from pathlib import Path
from abc import abstractmethod, ABC

from sxml import yaml_helpers
from .methods import SXML_BUILTINS

Namespace = dict[str, Any]
Config = Any


class Operator(ABC):
    def __init__(self, config: Config, namespace: Namespace) -> None:
        pass

    @abstractmethod
    def __call__(self, data, *, options):
        pass


class Chain(Operator):
    def __init__(self, config: Config, namespace: Namespace) -> None:
        super().__init__(config, namespace)
        self.namespace = namespace

        self._chain: list[Operator] = []
        for cfg in config:
            self.append(cfg)

    def append(self, cfg):
        if '$apply' in cfg:
            self._chain.append(Apply(cfg, self.namespace))
        elif '$map' in cfg:
            self._chain.append(Map(cfg, self.namespace))
        else:
            raise ValueError(f'unknown cfg type in chain: {cfg}')

    def __call__(self, data, *, options):
        for func in self._chain:
            data = func(data, options=options)
        return data

    @classmethod
    def from_options(cls, options, namespace):
        apply = options.pop('$apply', None)
        map_ = options.pop('$map', None)
        chain = options.pop('$chain', None)
        assert (apply is not None) + (map_ is not None) + (chain is not None) <= 1

        if apply:
            chain = [{'$apply': apply}]
        if map_:
            chain = [{'$map': map_}]
        if chain:
            return Chain(chain, namespace=namespace)
        return None


class Apply(Operator):
    def __init__(self, config: Config, namespace: Namespace) -> None:
        super().__init__(config, namespace)
        self.namespace = namespace
        name = config.pop('$apply')
        self.func = self.namespace[name](namespace=self.namespace, **config)

    def __call__(self, data, *, options):
        return self.func(data, options=options)


class Map(Operator):
    def __init__(self, config: Config, namespace: Namespace) -> None:
        super().__init__(config, namespace)
        self.namespace = namespace
        name = config.pop('$map')
        self.func = self.namespace[name](namespace=self.namespace, **config)

    def __call__(self, data, *, options):
        return [self.func(item, options=options) for item in data]


class HtmlPipeline(Chain):
    def __init__(self, config: Any) -> None:
        self._ns = GLOBALS
        if isinstance(config, list):
            config = {'$chain': config}
        super().__init__(config['$chain'], self._ns)

    def __call__(self, data, options=None):
        return super().__call__(data, options=options or {})

    @classmethod
    def from_file(cls, path: Union[str, Path], *args, **kwargs) -> 'HtmlPipeline':
        return cls.from_string(Path(path).read_text(*args, **kwargs))

    @classmethod
    def from_string(cls, config: str) -> 'HtmlPipeline':
        return cls(yaml_helpers.load(config))


GLOBALS: Namespace = {
    **SXML_BUILTINS,

    '$chain': Chain,
    '$map': Map,
    '$apply': Apply,
}

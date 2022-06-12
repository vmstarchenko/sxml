from typing import Callable, Optional, Union
from abc import abstractmethod, ABC
import collections
import json

from lxml import cssselect

from sxml.utils import lazy_import


jsonpath_ng = lazy_import("jsonpath_ng")


_CSS_TRANSLATOR = cssselect.LxmlHTMLTranslator()
QUERY_TYPES: dict[str, type] = {}


def css_to_xpath(query: str) -> str:
    return _CSS_TRANSLATOR.css_to_xpath(query)


def register(name: str) -> Callable[[type], type]:
    def wrapper(cls: type) -> type:
        QUERY_TYPES[name] = cls
        return cls
    return wrapper


class BaseQuery(ABC):
    @abstractmethod
    def __init__(self, query: str) -> None:
        pass

    @abstractmethod
    def apply(self, data):
        pass


@register('xpath')
class XPathQuery(BaseQuery):
    def __init__(self, query: str) -> None:
        self.query = query

    def apply(self, data):
        return (
            str(elt) if isinstance(elt, str) else elt
            for elt in data.xpath(self.query)
        )


@register('css')
class CssQuery(XPathQuery):
    def __init__(self, query: str) -> None:
        super().__init__(css_to_xpath(query))


@register('jpath')
class JPathQuery(BaseQuery):
    def __init__(self, query: str) -> None:
        self.query = jsonpath_ng.parse(query)

    def apply(self, data):
        return (x.value for x in self.query.find(data))


@register('const')
class ConstQuery(BaseQuery):
    def __init__(self, query: str) -> None:
        try:
            self.query = json.loads(query)
        except json.decoder.JSONDecodeError:
            self.query = query

    def apply(self, data):
        return [self.query]


class Query:
    def __init__(self, query: Union[Optional[str], list[Optional[str]]]) -> None:
        if isinstance(query, list):
            self._query = [self._parse_query(q) for q in query]
        else:
            self._query = [self._parse_query(query)]

    def __iter__(self):
        return iter(self._query)

    def apply(self, root):
        used_elts = set()
        elts = []
        for q in self._query:
            for elt in q.apply(root):
                if isinstance(elt, collections.abc.Hashable):
                    if elt not in used_elts:
                        elts.append(elt)
                        used_elts.add(elt)
                else:
                    elts.append(elt)
        return elts

    @staticmethod
    def _parse_query(query: Optional[str]) -> BaseQuery:
        if query is None:
            qtype, raw_query = 'xpath', '.'
        elif '|' not in query:
            qtype, raw_query = 'css', query
        else:
            qtype, raw_query = query.split('|', 1)
        return QUERY_TYPES[qtype](raw_query)

import re
import json
from typing import Any, Union, Optional
import datetime
from lxml import etree
import copy

from sxml.utils import wrap_global, lazy_import

from . import html

dateparser = lazy_import("dateparser")


class ReFindall:
    def __init__(self, *, pattern, namespace):
        self.regex = re.compile(pattern)

    def __call__(self, data, *, options):
        return self.regex.findall(data)


class ReSplit:
    def __init__(self, *, pattern, namespace):
        self.regex = re.compile(pattern)

    def __call__(self, data, *, options):
        return self.regex.split(data)


class ReSub:
    def __init__(self, *, pattern, repl, namespace):
        self.regex = re.compile(pattern)
        self.repl = repl

    def __call__(self, data, *, options):
        return self.regex.sub(self.repl, data)


class ReMatch:
    def __init__(self, *, pattern, namespace, group=None):
        self.regex = re.compile(pattern)
        self.group = group

    def get_func(self):
        return self.regex.match

    def __call__(self, data, *, options):
        match = self.get_func()(data)
        if match is None:
            return
        if self.group is None:
            return match.groupdict()
        return match.group(self.group)


class ReSearch(ReMatch):
    def get_func(self):
        return self.regex.search


def datetime_strftime(
    data: datetime.datetime,
    *,
    format: str = '%Y-%m-%dT%H:%M:%S'
) -> str:
    return data.strftime(format)


def datetime_fromtimestamp(data: Union[float, str]) -> datetime.datetime:
    if isinstance(data, str):
        data = float(data)
    return datetime.datetime.fromtimestamp(data)


def datetime_parse(
    data: str, *,
    now: Union[datetime.datetime, str, None] = None,
    timezone: str = 'UTC',
    to_timezone: str = 'UTC',
) -> Optional[datetime.datetime]:
    settings: Any = {
        'TIMEZONE': timezone,
        'TO_TIMEZONE': to_timezone,
        'RETURN_AS_TIMEZONE_AWARE': True,
    }
    if now is not None:
        if isinstance(now, str):
            now = dateparser.parse(now)
        settings['RELATIVE_BASE'] = now

    return dateparser.parse(data, settings=settings)


def tee(data):
    if isinstance(data, etree.ElementBase):
        text = html.html_dumps(data, pretty=True)
    else:
        text = str(data)
    print(text, flush=True)
    return data


class Hub:
    def __init__(self, *, namespace, merge: bool = False, **names):
        self.namespace = namespace
        self.names = [
            (name, self.namespace['$chain'](config, self.namespace))
            for name, config in names.items()
        ]
        self.merge = merge

    def __call__(self, data, *, options) -> dict:
        res = {
            name: func(
                data,
                options=options)
            for name, func in self.names
        }
        if not self.merge:
            return res

        return {
            k: v
            for val in res.values()
            if val
            for k, v in val.items()
        }


def copy_deepcopy(data):
    return copy.deepcopy(data)


def json_loads(data, **kwargs):
    return json.loads(data, **kwargs)


SXML_BUILTINS: dict[str, Any] = {
    'html.loads': wrap_global(html.html_loads),
    'html.dumps': wrap_global(html.html_dumps),
    'html.get_attr': wrap_global(html.html_get_attr),
    'html.remove': html.Remove,
    'html.split': html.Split,
    'html.extract_metadata': wrap_global(html.extract_metadata),
    'json.loads': wrap_global(json_loads),
    're.findall': ReFindall,
    're.split': ReSplit,
    're.sub': ReSub,
    're.match': ReMatch,
    're.search': ReSearch,
    'datetime.strftime': wrap_global(datetime_strftime),
    'datetime.fromtimestamp': wrap_global(datetime_fromtimestamp),
    'datetime.parse': wrap_global(datetime_parse),
    'sxml.find': html.Find,
    'copy.deepcopy': wrap_global(copy_deepcopy),
    'tee': wrap_global(tee),
    'hub': Hub,
    'int': wrap_global(int)
}

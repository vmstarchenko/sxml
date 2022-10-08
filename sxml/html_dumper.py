import pathlib
import json
import os
import time

import lxml.html
import lxml.etree


class HtmlDumper:
    STYLE = '''
    body { background: #F5F5F5; font-family: consolas, monospace; font-style: normal; font-weight: bold }
    *[type=key] { color: brown; }
    *[type=str] { color: darkgreen; }
    *[type=NoneType] { color: purple; }
    *[type=html] summary { padding-left: 1em; background: yellow; }
    *[type=brace] { font-weight: bolder }
    *[type=brace][level="0"] { color: black }
    *[type=brace][level="1"] { color: red }
    *[type=brace][level="2"] { color: green }
    *[type=brace][level="3"] { color: cyan }
    *[type=brace][level="4"] { color: orange }
    *[type=brace][level="5"] { color: brown }
    *[type=brace][level="6"] { color: lightgreen }
    *[type=brace][level="7"] { color: blue }
    *[type=brace][level="8"] { color: #FF00FF }
    *[type=brace][level="9"] { color: purple }
    '''
    def __init__(self, indent=None, allow_unicode=False, sort_keys=False, output=None, **kwargs):
        self.indent = indent
        self.allow_unicode = allow_unicode
        self.sort_keys = sort_keys
        self.output = output
        self._data_iter = iter(range(1000))

    def get_unique_id(self):
        return next(self._data_iter)

    def get_data_path(self):
        assert isinstance(self.output, (str, pathlib.Path)), type(self.output)
        out_dir = f'{str(self.output)}.data'
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        return os.path.join(out_dir, f'{self.get_unique_id()}.html')

    def convert(self, data):
        return self._node([
            self._node(text=self.STYLE, tag='style'),
            self._node(self._to_html(data), 'body'),
        ], tag='html')

    def _node(self, children=None, tag='div', attrs=None, text=None, tail=None):
        elt = lxml.html.Element(tag)
        if children is not None:
            assert isinstance(children, list), children
            for child in children:
                elt.append(child)
        if attrs is not None:
            indent = attrs.get('indent')
            if indent is not None and self.indent is not None:
                attrs['style'] = attrs.get('style', '') + f'padding-left: {indent*self.indent/4}em;'
            elt.attrib.update({key: str(val) for key, val in attrs.items()})
        elt.text = text
        elt.tail = tail
        return elt

    def add_comma(self, add):
        return [] if not add else [self._node(text=',', tag='span')]

    def _to_html(self, data, level=0, add_comma=False):
        if isinstance(data, dict):
            return [
                self._node(text='{', tag='span', attrs={'level': level, 'type': 'brace'}),
                self._node([
                    self._node(
                        [
                            self._node([
                                self._node(
                                    text=json.dumps(str(key)),
                                    tag='span',
                                    tail=' : ',
                                    attrs={'type': 'key'},
                                ),
                                *self._to_html(value, level=level+1, add_comma=i<len(data)),
                            ])
                            for i, (key, value) in enumerate(data.items(), 1)
                        ], attrs={'indent': 1}),
                    ],
                    attrs={'type': 'dict'},
                ),
                self._node(text='}', tag='span', attrs={'level': level, 'type': 'brace'}),
                *self.add_comma(add_comma),
            ]

        if isinstance(data, list):
            return [
                self._node(text='[', tag='span', attrs={'level': level, 'type': 'brace'}),
                self._node([
                    self._node(
                        [
                            self._node(self._to_html(
                                item,
                                add_comma=i<len(data),
                                level=level+1,
                            ), attrs={'indent': 1})
                            for i, item in enumerate(data, 1)
                        ],
                    ),
                ], attrs={'type': 'list'}),
                self._node(text=']', tag='span', attrs={'level': level, 'type': 'brace'}),
                *self.add_comma(add_comma),
            ]

        if isinstance(data, lxml.etree.ElementBase):
            data_path = self.get_data_path()
            with open(data_path, 'w', encoding='utf-8') as f:
                f.write(lxml.html.tostring(data, pretty_print=True, encoding='unicode'))
            return [self._node(
                [
                    self._node(self.add_comma(add_comma), text=repr(data), tag='summary'),
                    self._node([data], tag='iframe', attrs={
                        'src': f'{data_path}?ts={time.time()}',
                        'width': '100%', 'height': '500px',
                    }),
                ],
                tag='details',
                attrs={'indent': 1, 'type': 'html'},
            )]

        return [
            self._node(text=json.dumps(data), tag='span', attrs={'type': type(data).__name__}),
            *self.add_comma(add_comma),
        ]

    def dump(self, data):
        return lxml.html.tostring(self.convert(data), pretty_print=True, encoding='unicode')

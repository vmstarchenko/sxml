from typing import Any, Union, Optional
import subprocess as sp

from lxml import html as htree
from bs4 import BeautifulSoup    # type: ignore
import extruct    # type: ignore

from sxml.query import Query
from sxml.utils import clean_spaces


FORMAT_JS_CMD = ['clang-format']


def format_js(script: str):
    proc = sp.Popen(FORMAT_JS_CMD, stdin=sp.PIPE, stdout=sp.PIPE)
    out, err = proc.communicate(script.encode('utf8'))
    proc.kill()
    if proc.returncode:
        return script
    return f'\n{out.decode("utf8").strip()}\n'


def prettify_scripts(html: str) -> str:
    parser = htree.HTMLParser()
    tree = htree.fromstring(html, parser=parser)
    for node in tree.xpath('.//script'):
        node.text = format_js(node.text)
    return htree.tostring(tree.body, encoding='unicode')


def prettify_html(html: str) -> str:
    return next(BeautifulSoup(html, 'lxml').body.children).prettify()


def prettify(html: Optional[str]) -> Optional[str]:
    if html is None:
        return None
    return prettify_html(prettify_scripts(html))


def html_loads(data, *, url=None) -> htree.Element:
    tree = htree.fromstring(data)
    base_urls = tree.xpath('.//base/@href')
    base_url = base_urls[0] if base_urls else url
    if base_url:
        tree.make_links_absolute(base_url)
    return tree


def html_dumps(
    data, *,
    raw: bool = None, clean: bool = None, pretty: bool = False,
) -> Union[str, None]:
    if pretty and (clean or raw is False):
        raise ValueError
    if raw is None:
        raw = True if pretty else False
    if clean is None:
        clean = False if raw else True

    if data is None:
        return None

    if raw:
        res = htree.tostring(
            data, encoding='unicode',
        )
        if pretty:
            res = prettify(res)
        return res

    res = ''.join(data.xpath('self::*//text()'))
    if clean:
        res = clean_spaces(res)
    return res


def html_get_attr(data, *, name: str) -> str:
    return data.attrib[name]


class Remove:
    def __init__(self, query, namespace):
        self.namespace = namespace
        self.query = Query(query)

    def __call__(self, data, *, options):
        for query in self.query:
            for node in query.apply(data):
                if not self.remove_node(node):
                    return
        return data

    @staticmethod
    def remove_node(elt):
        parent = elt.getparent()
        if parent is None:
            return False
        tail = elt.tail or '\n'
        prev = elt.getprevious()
        if prev is not None:
            prev.tail = (prev.tail or '') + tail
        else:
            parent.text = (parent.text or '') + tail
        parent.remove(elt)
        return True


class Split:
    def __init__(self, query, namespace, *, as_list=False):
        self.namespace = namespace
        self.query = Query(query)
        self.as_list = as_list

    def __call__(self, data, *, options):
        nodes = set(self.query.apply(data))
        children = list(data)

        cur_node = htree.Element('split_element')
        cur_node.text = data.text

        res = []
        for child in children:
            if child in nodes:
                if (cur_node.text and cur_node.text.strip()) or list(cur_node):
                    res.append(cur_node)

                cur_node = htree.Element('split_item')
            cur_node.append(child)

        if (cur_node.text and cur_node.text.strip()) or list(cur_node):
            res.append(cur_node)

        if self.as_list:
            return res

        res_node = htree.Element('split_root')
        res_node.extend(res)
        return res_node


class Find:
    def __init__(self, *, attrs, namespace):
        self.namespace = namespace

        self.attrs = []
        for attr in attrs:
            many = attr.get('many', False)
            chain = self.namespace['$chain'].from_options(attr, self.namespace)

            sub_attrs = attr.get('attrs')
            if sub_attrs:
                if not chain:
                    chain = self.namespace['$chain']([], self.namespace)

                if many:
                    chain.append({'$map': 'sxml.find', 'attrs': sub_attrs})
                else:
                    chain.append({'$apply': 'sxml.find', 'attrs': sub_attrs})

            self.attrs.append({
                'many': many,
                'name': attr['name'],
                'required': attr.get('required', False),
                'query': Query(attr.get('query')),
                'chain': chain,
            })

    def __call__(self, data: htree.Element, *, options) -> dict[str, Any]:
        return {
            attr['name']: self._find_attr(data, attr, options)
            for attr in self.attrs
        }

    def _find_attr(
        self, tree: htree.Element, attr: dict, options
    ) -> Union[list[Any], Optional[Any]]:

        chain = attr['chain']
        elts = attr['query'].apply(tree)

        res: Union[list[Any], Optional[Any]]
        if attr['many']:
            res = list(elts)
            # values = list(filter(None, (sub_attrs(v, options=options) for v in values)))
        else:
            res = next(iter(elts), None) if elts else None

        if chain:
            res = chain(res, options=options)

        if res is None and attr['required']:
            raise

        return res


# https://github.com/scrapinghub/extruct
def extract_metadata(
    data, *,
    url: Optional[str] = None,
    formats: Optional[list[str]] = extruct.SYNTAXES,
) -> dict[str, Any]:
    metadata = extruct.extract(data, base_url=url, syntaxes=formats, uniform=True)
    metadata = {
        key: value
        for key, value in metadata.items()
        if value and any(any(v.values()) for v in value)
    }
    return metadata

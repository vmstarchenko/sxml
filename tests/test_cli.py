# flake8: noqa: F501

import yaml
import sxml.cli
import json
import pytest
from pathlib import Path

SIMPLE_CONFIG = r'''
$chain:
  - $apply: html.loads
  - $apply: sxml.find
    attrs:
      - name: title
        query: h1
        $chain:
          - $apply: html.dumps
'''


def test_simple(tmp_path):
    config_path = tmp_path / 'simple_config.yaml'
    config_path.write_text(SIMPLE_CONFIG)

    inp_path = tmp_path / 'inp.html'
    inp_path.write_text('<h1>hello</h1>')

    out_path = tmp_path / 'out.html'

    args = sxml.cli.parse_args([
        '-p', str(config_path),
        '-i', str(inp_path),
        '-o', str(out_path),
        '-e', json.dumps({'url': 'https://example.com'}),
    ])

    sxml.cli.main(args)

    assert yaml.safe_load(out_path.read_text()) == {
        'title': 'hello',
    }


# sxml -p ./examples/wordnet.yaml -i ./examples/wordnet.html -o ./examples/wordnet.out.yaml -e '{"url": "http://wordnetweb.princeton.edu/perl/webwn?s=royal"}' -SUN 4
# python -m sxml -p ./examples/wiktionary.yaml -i ./examples/wiktionary.html -o ./examples/wiktionary.out.yaml -e '{"url": "https://en.wiktionary.org/wiki/head"}' -SUN 4
# sxml -p ./examples/python_releases.yaml -i ./examples/python_releases.html -o ./examples/python_releases.out.yaml -e '{"url": "https://www.python.org/downloads/source/"}' -SUN 4
# sxml -p ./examples/pypi.yaml -i ./examples/pypi.html -o ./examples/pypi.out.yaml -e '{"url": "https://pypi.org/project/lxml/"}' -SUN 4

EXAMPLES_OPTIONS = {
    'python_releases': [
        '-SUN', '4',
        '-e', json.dumps({"url": "https://www.python.org/downloads/source/"}),
    ],
    'wiktionary': [
        '-SUN', '4',
        '-e', json.dumps({"url": "https://en.wiktionary.org/wiki/head"}),
    ],
    'wordnet': [
        '-SUN', '4',
        '-e', json.dumps({"url": "http://wordnetweb.princeton.edu/perl/webwn?s=royal"}),
    ],
    'pypi': [
        '-SUN', '4',
        '-e', json.dumps({"url": "https://pypi.org/project/lxml/"}),
    ],
}

@pytest.mark.parametrize("name", [
    'python_releases',
    'wiktionary',
    'wordnet',
    'pypi',
])
def test_examples(name, tmp_path):
    examples_path = Path(__file__).parent.parent / 'examples'
    config_path = examples_path / f'{name}.yaml'
    inp_path = examples_path / f'{name}.html'

    out_path = tmp_path / 'out.html'
    args = sxml.cli.parse_args([
        '-p', str(config_path),
        '-i', str(inp_path),
        '-o', str(out_path),
        *EXAMPLES_OPTIONS[name],
    ])

    sxml.cli.main(args)

    assert out_path.read_text() == (examples_path / f'{name}.out.yaml').read_text()

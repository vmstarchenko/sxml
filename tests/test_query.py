import textwrap
import sxml


def test_const_query():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: key1
                query: const|key1
              - name: key2
                query: const|"key2"
              - name: key3
                query: 'const|{"key3": 3}'
    '''))

    assert parse('<div></div>', options={
        'url': 'https://example.com',
    }) == {'key1': 'key1', 'key2': 'key2', 'key3': {'key3': 3}}


def test_json_query():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: json
                query: div
                $chain:
                  - $apply: html.dumps
                    clean: false
                  - $apply: re.match
                    pattern: 'var example=(.*)'
                    group: 1
                  - $apply: json.loads
          - $apply: sxml.find
            attrs:
              - name: key2
                query: jpath|json.key1.key2
                many: true

    '''))

    assert parse(
        '<div>var example={"key1": {"key2": "some  string  value"}}</div>',
        options={'url': 'https://example.com'}
    ) == {'key2': ['some  string  value']}

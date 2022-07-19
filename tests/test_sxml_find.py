import textwrap
import sxml


def test_simple():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: title
                query: h1
                $chain:
                  - $apply: html.dumps
    '''))

    assert parse('<h1>hello</h1>', options={'url': 'https://example.com'}) == {
        'title': 'hello',
    }


def test_sub_attrs():
    html = r'''
    <html>
      Hello
      <body>
        <h1>title</h1>
        <a href="http://link1">link1</a>
        <a href="http://link2">link2</a>
      </body>
    </html>
    '''

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: content
                query: body
                attrs:
                  - name: links
                    many: true
                    query: xpath|.//a
                    $chain:
                      - $map: html.get_attr
                        name: href
    '''))

    assert parse(
        html,
        options={'url': 'https://example.com'}) == {
        'content': {'links': ['http://link1', 'http://link2']}
    }

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: links
                query: a
                many: true
                attrs:
                  - name: title
                    query: xpath|./text()
                  - name: url
                    query: xpath|./@href
    '''))

    assert parse(
        html,
        options={'url': 'https://example.com'}) == {
            'links': [
                {'title': 'link1', 'url': 'http://link1'},
                {'title': 'link2', 'url': 'http://link2'}
            ]
        }

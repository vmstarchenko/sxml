import textwrap
import sxml
import pytest
import yaml
import json


def test_loads():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.dumps
            raw: true
    '''))

    assert parse(r'''<html><body>valid</body></html>''', options={
        'url': 'http://localhost'
    }) == '<html><body>valid</body></html>'

    assert parse(r'''<html><body>broken''', options={
        'url': 'http://localhost'
    }) == '<html><body>broken</body></html>'

    assert parse(r'''<body>no html</body>''', options={
        'url': 'http://localhost'
    }) == '<span>no html</span>'

    assert parse(r'''<body>no html <div>nested</div></body>''', options={
        'url': 'http://localhost'
    }) == '<div>no html <div>nested</div></div>'

    assert parse(r'''not html''', options={
        'url': 'http://localhost'
    }) == '<p>not html</p>'

    assert parse(r'''not html <div>nested</div>''', options={
        'url': 'http://localhost'
    }) == '<div><p>not html </p><div>nested</div></div>'


def test_loads_dup_keys():
    with pytest.raises(ValueError):
        parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
            $chain:
              - $apply: html.loads
                $apply: html.dumps
                raw: true
        '''))


def test_loads_input_params():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
            url: !Opt url
          - $apply: sxml.find
            attrs:
              - name: link
                query: xpath|.//a/@href
    '''))

    assert parse('<div><a href="/ok_url">text</a></div>', options={
        'url': 'http://localhost',
    }) == {'link': 'http://localhost/ok_url'}


    with pytest.raises(KeyError):
        assert parse('<div><a href="/missed_url">text</a></div>') == {'link': '/missed_url'}

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: link
                query: xpath|.//a/@href
    '''))

    assert parse('<div><a href="/missed_url">text</a></div>') == {'link': '/missed_url'}

    assert parse(textwrap.dedent(r'''
        <html>
            <head><base href="http://localhost" /></head>
            <body><a href="/base_url" /></body>
        </html>
    ''')) == {'link': 'http://localhost/base_url'}



def test_dumps():
    data = r'''<body> <h1>title</h1> content1 <div>hello  world</div></body>'''
    options={
        'url': 'http://localhost'
    }

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.dumps
    '''))
    assert parse(data, options=options) == 'title content1 hello world'

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.dumps
            clean: false
    '''))
    assert parse(data, options=options) == ' title content1 hello  world'

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.dumps
            raw: true
    '''))
    assert parse(data, options=options) == '<div> <h1>title</h1> content1 <div>hello  world</div></div>'


def test_re_match():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: re.match
            pattern: some (?P<w1>.*) (?P<w2>.*)
    '''))
    assert parse("some other string") == {'w1': 'other', 'w2': 'string'}

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: re.match
            pattern: some (?P<value>.*)
            group: value
    '''))
    assert parse("some string") == 'string'

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: re.match
            pattern: some (?P<value>oops)
    '''))
    assert parse("some string") == None


def test_remove():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.remove
            query: [css|ads1, xpath|.//ads2]
          - $apply: html.dumps
    '''))
    assert parse(r'''
        <body>
            <ads1>BadString</ads1>
            <h1>title</h1>
            <ads1>BadString</ads1>
            <ads1>BadString</ads1>
            content1
            <ads2>BadString</ads2>
            content2
        </body>
    ''', options={'url': 'http://localhost'}) == 'title content1 content2'

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.remove
            query: [div]
          - $apply: html.remove
            query: [div]
          - $apply: html.dumps
    '''))
    assert parse('''
        <div><a>hello</a></div>
    ''', options={'url': 'http://localhost'}) is None


def test_split():
    html = textwrap.dedent(r'''
    <div>
        <h1>title1</h1>
        content1
        <p>text</p>
        <h2>title2</h2>
        <p>content1</p>
        text
    </div>
    ''')
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: content
                query: div
                $chain:
                  - $apply: html.split
                    query: h1,h2
                    as_list: true
                    drop_first: 0
                  - $map: html.dumps
    '''))
    assert parse(html, options={'url': 'http://localhost'}) == {
        'content': [
            'title1 content1 text',
            'title2 content1 text'
        ]
    }

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: content
                query: div
                $chain:
                  - $apply: html.split
                    query: h1,h2
                    as_list: true
                  - $map: html.dumps
    '''))
    assert parse(html, options={'url': 'http://localhost'}) == {
        'content': [
            'title2 content1 text'
        ]
    }

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: content
                query: div
                $chain:
                  - $apply: html.split
                    query: h1,h2
                    as_list: true
                    drop_first: 0
                    drop_last: 1
                  - $map: html.dumps
    '''))
    assert parse(html, options={'url': 'http://localhost'}) == {
        'content': [
            'title1 content1 text'
        ]
    }


    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: content
                query: div
                $chain:
                  - $apply: html.split
                    query: h1,h2
                    drop_first: 0
                  - $apply: html.dumps
                    raw: true
    '''))
    assert parse(
        html,
        options={'url': 'http://localhost'}
    )['content'] == textwrap.dedent('''\
        <split_root><split_item><h1>title1</h1>
            content1
            <p>text</p>
            </split_item><split_item><h2>title2</h2>
            <p>content1</p>
            text
        </split_item></split_root>''')


def test_get_attr():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: a
                query: a
                $chain:
                  - $apply: html.get_attr
                    name: href
    '''))

    assert parse(r'''<div><a href="https://localhost">valid</a></div>''') == {
        'a': 'https://localhost'
    }

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: sxml.find
            attrs:
              - name: a
                query: xpath|./a/@href
    '''))

    assert yaml.dump(parse(
        r'''<div><a href="https://localhost">valid</a></div>'''
    )) == 'a: https://localhost\n'


def test_html_dumps_pretty():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: html.dumps
            pretty: true
    '''))

    assert parse(
        r'''<div><script>var x=1</script><a href="https://localhost">valid</a></div>'''
    ) == textwrap.dedent(
        '''
        <div>
         <script>
          var x = 1
         </script>
         <a href="https://localhost">
          valid
         </a>
        </div>
        '''
    ).strip()


def test_html_extract_metadata():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.extract_metadata
    '''))
    jld = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "url": "https://www.python.org/",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://www.python.org/search/?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    }

    assert parse(
        rf'''
        <div>
           <script type="application/ld+json">
               {json.dumps(jld)}
           </script>
        </div>
        '''
    ) == {
        'json-ld': [jld]
    }


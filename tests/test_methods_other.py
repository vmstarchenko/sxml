import textwrap
import sxml


def test_tee(capsys):
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: html.loads
          - $apply: tee
          - $apply: html.dumps
            raw: true
    '''))
    assert parse('<div>hello</div>') == '<div>hello</div>'
    captured = capsys.readouterr()
    assert captured.out == textwrap.dedent(
        '''\
        <div>
         hello
        </div>
        ''')


def test_copy_deepcopy():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
    $chain:
      - $apply: html.loads
      - $apply: sxml.find
        attrs:
          - name: body
            query: div
            attrs:
              - name: cleaned_elt
                $chain:
                  - $apply: html.remove
                    query: a
                  - $apply: html.dumps
              - name: full_elt
                $apply: html.dumps
    '''))
    assert parse('<div>hello<a>oops</a></div>') == {
        'body': {'cleaned_elt': 'hello', 'full_elt': 'hello'}
    }

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
    $chain:
      - $apply: html.loads
      - $apply: sxml.find
        attrs:
          - name: body
            query: div
            attrs:
              - name: cleaned_elt
                $chain:
                  - $apply: copy.deepcopy
                  - $apply: html.remove
                    query: a
                  - $apply: html.dumps
              - name: full_elt
                $apply: html.dumps
    '''))
    assert parse('<div>hello<a>oops</a></div>') == {
        'body': {'cleaned_elt': 'hello', 'full_elt': 'hellooops'}
    }


def test_hub():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: hub
            f1:
              - $apply: html.loads
              - $apply: html.dumps
            f2:
              - $apply: html.loads
              - $apply: html.dumps
                raw: true
    '''))
    assert parse('<div>hello</div>') == {
        'f1': 'hello',
        'f2': '<div>hello</div>',
    }

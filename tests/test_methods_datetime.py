import datetime
import textwrap
import sxml
import pytest
from freezegun import freeze_time

UTC = datetime.timezone.utc
UTC4 = datetime.timezone(datetime.timedelta(hours=4))
UTC_4 = datetime.timezone(datetime.timedelta(hours=-4))


def test_strftime():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.strftime
    '''))
    assert parse(datetime.datetime(2000, 1, 2, 3, 4, 5)) == '2000-01-02T03:04:05'

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.strftime
            format: '%Y/%m/%d'
    '''))
    assert parse(datetime.datetime(2000, 1, 2, 3, 4, 5)) == '2000/01/02'


def test_fromtimestamp():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.fromtimestamp
    '''))
    assert parse(946771445) == datetime.datetime(2000, 1, 2, 3, 4, 5)

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.fromtimestamp
    '''))
    assert parse('946771445.000') == datetime.datetime(2000, 1, 2, 3, 4, 5)


@freeze_time('2000-01-02T03:04:05+0000')
def test_parse():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
    '''))
    assert parse('2000-01-02T03:04:05+0000') == datetime.datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC)

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
    '''))
    assert parse('Now') == datetime.datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC)

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
            timezone: '+0400'
    '''))
    assert parse('Now GMT') == datetime.datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC)


@freeze_time(datetime.datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC_4))
def test_parse_other_timezone():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
    '''))
    assert parse('2000-01-02T03:04:05+0000') == datetime.datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC)

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
    '''))
    assert parse('Now') == datetime.datetime(2000, 1, 2, 7, 4, 5, tzinfo=UTC)

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
            timezone: '+0800'
    '''))
    assert parse('Now') == datetime.datetime(2000, 1, 2, 7, 4, 5, tzinfo=UTC)


@freeze_time(datetime.datetime(2000, 1, 2, 3, 4, 5, tzinfo=UTC))
def test_parse_other_base():
    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
            now: '2001-02-03T04:05:06'
    '''))
    assert parse('Now') == datetime.datetime(2001, 2, 3, 4, 5, 6, tzinfo=UTC)

    parse = sxml.HtmlPipeline([{
        '$apply': 'datetime.parse',
        'now': datetime.datetime(2001, 2, 3, 4, 5, 6)
    }])
    assert parse('Now') == datetime.datetime(2001, 2, 3, 4, 5, 6, tzinfo=UTC)

    parse = sxml.HtmlPipeline.from_string(textwrap.dedent(r'''
        $chain:
          - $apply: datetime.parse
            now: !Opt now_option
    '''))
    now = datetime.datetime(2003, 2, 3, 4, 5, 6, tzinfo=UTC)
    assert parse('Now', options={'now_option': now}) == now

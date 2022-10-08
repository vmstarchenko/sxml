import argparse
import json
import pathlib
import sys

import sxml
from sxml import yaml_helpers

from .html_dumper import HtmlDumper

FORMATS = ['json', 'yaml', 'html']


DUMPERS = {
    'json': lambda *args, allow_unicode=False, indent=None, sort_keys=False, **kwargs: json.dumps(
        *args, ensure_ascii=not allow_unicode, indent=indent, sort_keys=sort_keys,
    ),
    'yaml': lambda data, *args, allow_unicode=False, indent=None, sort_keys=False, **kwargs: \
            yaml_helpers.dump(
                data, allow_unicode=allow_unicode, indent=indent, sort_keys=sort_keys
            ),
    'html': lambda data, *args, **kwargs: HtmlDumper(*args, **kwargs).dump(data),
}

def parse_args(args=None):
    parser = argparse.ArgumentParser(description='Convert json to json.')
    parser.add_argument(
        '-p', '--pipeline',
        required=True,
        type=pathlib.Path,
        help='html pipline path'
    )
    parser.add_argument(
        '-i', '--input',
        type=pathlib.Path,
        help='input html path (stdin by default)'
    )
    parser.add_argument(
        '-o', '--output',
        type=pathlib.Path,
        help='output yaml/json path (stdout by default)'
    )

    parser.add_argument(
        '-O', '--output-format',
        choices=FORMATS,
    )

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-e', '--extra-options', type=json.loads, default={})

    parser.add_argument('-S', '--sort-keys', action='store_true')
    parser.add_argument('-U', '--allow-unicode', action='store_true')
    parser.add_argument('-N', '--indent', type=int)

    return parser.parse_args(args) if args else parser.parse_args()


def main(args):
    Dumper = yaml_helpers.DebugDumper if args.debug else yaml_helpers.Dumper

    pipeline = args.pipeline
    if args.input is None:
        input_text = sys.stdin.read()
    else:
        input_text = args.input.read_text()

    if args.output is None:
        output_suffix = None
    else:
        output_suffix = args.output.suffix.strip('.')
        output_suffix = output_suffix if output_suffix in FORMATS else None

    output_format = args.output_format or output_suffix or 'yaml'

    output_data = sxml.HtmlPipeline.from_file(pipeline)(input_text, options=args.extra_options)
    output_text = DUMPERS[output_format](
        output_data,
        indent=args.indent,
        allow_unicode=args.allow_unicode,
        sort_keys=args.sort_keys,
        Dumper=Dumper,
        output=args.output,
    )

    if args.output is None:
        sys.stdout.write(output_text)
    else:
        args.output.write_text(output_text)

"""
Make conferatur available through a jsonapi interface
"""

from flask import Flask
from flask_jsonrpc import JSONRPC
import argparse

app = Flask(__name__)
jsonrpc = JSONRPC(app, '/api', enable_web_browsable_api=True)


def argparser(parser=None) -> argparse.ArgumentParser:
    if parser is None:
        parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', default=False,
                        help="enable flask debug mode")
    return parser


def main(parser, args):
    app.run(debug=args.debug)


if __name__ == '__main__':
    _parser = argparser()
    main(_parser, _parser.parse_args())
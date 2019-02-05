import textwrap
import inspect
import re
from collections import namedtuple

Docblock = namedtuple('Docblock', ['docs', 'params', 'result', 'result_type'])
DocblockParam = namedtuple('DocblockParam', ['name', 'type', 'type_doc', 'is_required', 'description'])


def format_docs(docs):
    return textwrap.dedent(docs).strip()


def parse(func):
    docs = format_docs(func.__doc__)

    argspec = inspect.getfullargspec(func)
    args = list(argspec.args)

    if len(args) and args[0] in ('self', 'cls'):
        args.pop(0)

    defaults_idx = len(args) - (len(argspec.defaults) if argspec.defaults else 0)

    doc_params = {}
    doc_result = None
    doc_result_type = None

    def doc_param_parser(match):
        nonlocal doc_params
        type_, name, description = match[1], match[2], match[3]
        doc_params[name] = [type_, description]
        return ''

    def doc_result_parser(match):
        nonlocal doc_result_type, doc_result
        doc_result_type, doc_result = match[1], match[2]
        return ''

    docs = re.sub(r'^\s*:param\s+(?:([^:]+)\s+)?([a-z_]+): (.*)$', doc_param_parser, docs, flags=re.MULTILINE).strip()
    docs = re.sub(r'^\s*:return\s([a-z_]+): (.*)?', doc_result_parser, docs, flags=re.MULTILINE).strip()

    params = []
    for idx, name in enumerate(args):
        type_ = None
        description = ''
        if name in doc_params:
            type_, description = doc_params[name]
        param = DocblockParam(name,
                              argspec.annotations[name] if name in argspec.annotations else None,
                              type_,
                              idx < defaults_idx,
                              description
                              )
        params.append(param)

    result = Docblock(docs=docs, params=params, result=doc_result, result_type=doc_result_type)
    return result



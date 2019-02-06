import textwrap
import inspect
import re
from collections import namedtuple

Docblock = namedtuple('Docblock', ['docs', 'params', 'result', 'result_type'])
Param = namedtuple('Param', ['name', 'type', 'type_doc', 'is_required', 'description', 'example'])
DocblockParam = namedtuple('DockblockParam', ['name', 'type', 'value'])


def format_docs(docs):
    return textwrap.dedent(docs).strip()


def doc_param_parser(docstring, key, no_name=None):
    results = None if no_name else {}

    def _(match):
        nonlocal results, key, no_name
        if no_name:
            results = DocblockParam(key, match[1], match[2])
        else:
            results[match[1]] = DocblockParam(match[1], match[2], match[3])
        return ''

    if no_name:
        regex = r'^\s*:%s\s*([a-z_]+)?:(?:\s+(.*))?$'
    else:
        regex = r'^\s*:%s\s+(?:([^:]+)\s+)?([a-z_]+):(?:\s+(.*))?$'

    docs = re.sub(regex % (re.escape(key),), _, docstring, flags=re.MULTILINE).strip()

    return docs, results


def parse(func):
    docs = format_docs(func.__doc__)

    argspec = inspect.getfullargspec(func)
    args = list(argspec.args)

    if len(args) and args[0] in ('self', 'cls'):
        args.pop(0)

    defaults_idx = len(args) - (len(argspec.defaults) if argspec.defaults else 0)

    docs, doc_params = doc_param_parser(docs, 'param')
    docs, doc_result = doc_param_parser(docs, 'return', True)
    docs, examples = doc_param_parser(docs, 'example')

    params = []
    for idx, name in enumerate(args):
        type_ = None
        description = ''
        if name in doc_params:
            type_ = doc_params[name].type
            description = doc_params[name].value

        param = Param(name,
                      argspec.annotations[name] if name in argspec.annotations else None,
                      type_,
                      idx < defaults_idx,
                      description,
                      examples[name] if name in examples else None)
        params.append(param)

    result = Docblock(docs=docs, params=params,
                      result=doc_result.value if doc_result else None,
                      result_type=doc_result.type if doc_result else None)
    return result



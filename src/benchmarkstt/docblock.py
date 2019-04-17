import textwrap
import inspect
import re
import ast
from collections import namedtuple
import logging
from docutils.core import publish_string
from docutils.writers import html5_polyglot
import docutils


logger = logging.getLogger(__name__)

Docblock = namedtuple('Docblock', ['docs', 'params', 'result', 'result_type'])
Param = namedtuple('Param', ['name', 'type', 'type_doc', 'is_required',
                             'description', 'examples'])
DocblockParam = namedtuple('DocblockParam', ['name', 'type', 'value'])


def format_docs(docs):
    return textwrap.dedent(docs).strip()


def doc_param_parser(docstring, key, no_name=None, allow_multiple=None,
                     replace_strat=None):
    results = [] if no_name or allow_multiple else {}

    if replace_strat is None:
        def replace_strat(match, param):
            return match.group(0)
    elif type(replace_strat) is str:
        _replace_strat = replace_strat

        def replace_strat(match, param):
            nonlocal _replace_strat
            return _replace_strat

    def _(match):
        nonlocal results, key, no_name, replace_strat
        if no_name:
            param = dict(name=key, type=match.group(1), value=match.group(2))
            return_val = replace_strat(match, param)
            results.append(DocblockParam(**param))
        else:
            value = textwrap.dedent(match.group(3)).strip()
            param = dict(name=match.group(2), type=match.group(1), value=value)
            return_val = replace_strat(match, param)
            param = DocblockParam(**param)
            if allow_multiple:
                # check if it already exists, if not create a new object
                idx = [idx for idx, val in enumerate(results)
                       if match.group(2) not in val]
                if not len(idx):
                    idx = len(results)
                    results.append({})
                else:
                    idx = idx[0]
                results[idx][match.group(2)] = param
            else:
                results[match.group(2)] = param

        return return_val

    if no_name:
        regex = r'^[ \t]*:%s[ \t]*([a-z_]+)?:[ \t]+(.*)$'
    else:
        regex = r'^[ \t]*:%s[ \t]+(?:([^:]+)[ \t]+)?([a-z_]+):[ \t]*(.+$|(?:$[ \t]*\n)*([ \t]+)([^\n]*)$(?:\4.*\n|\n)+)'

    docs = re.sub(
        regex % (re.escape(key),), _, docstring, flags=re.MULTILINE
    ).strip()

    return docs, results


def decode_literal(txt: str):
    if txt is None:
        return ''

    try:
        return ast.literal_eval(txt)
    except (ValueError, SyntaxError) as e:
        logger.warning('%s "%s" for: %s', type(e), e, txt)
        return txt


def parse(func):
    docs = format_docs(func.__doc__)

    argspec = inspect.getfullargspec(func)
    args = list(argspec.args)

    if len(args) and args[0] in ('self', 'cls'):
        args.pop(0)

    defaults_idx = len(args) - (len(argspec.defaults) if argspec.defaults else 0)

    docs, doc_params = doc_param_parser(docs, 'param', replace_strat='')
    docs, doc_result = doc_param_parser(docs, 'return', no_name=True)

    def decode_examples(match, param):
        if match.group(5) is None:
            param['value'] = decode_literal(param['value'])
        else:
            param['value'] = process_rst(param['value'], 'text')
        return ''

    docs, examples = doc_param_parser(docs, 'example', allow_multiple=True,
                                      replace_strat=decode_examples)

    params = []
    for idx, name in enumerate(args):
        type_ = None
        description = ''
        if name in doc_params:
            type_ = doc_params[name].type
            description = doc_params[name].value

        param = Param(name,
                      argspec.annotations[name] if name in argspec.annotations
                      else None,
                      type_,
                      idx < defaults_idx,
                      description,
                      examples)

        params.append(param)

    # quick hack to remove this
    docs = docs.replace(':py:class:', '')

    result = Docblock(docs=docs, params=params,
                      result=doc_result[0].value if doc_result else None,
                      result_type=doc_result[0].type if doc_result else None)
    return result


class HTML5Writer(html5_polyglot.Writer):
    def apply_template(self):
        subs = self.interpolation_dict()
        return subs['body']


class TextWriter(docutils.writers.Writer):
    class TextVisitor(docutils.nodes.SparseNodeVisitor):
        _text = ''

        def visit_Text(self, node):
            self._text += node.astext()

        def visit_paragraph(self, node):
            self._text += '\n\n'

        def text(self):
            return self._text

    def translate(self):
        visitor = self.TextVisitor(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.text()


def process_rst(text, writer=None):
    if writer is None or writer == 'html':
        writer = HTML5Writer()
    elif writer == 'text':
        writer = TextWriter()
    elif type(writer) is str:
        raise ValueError("Unknown writer %s", str)
    settings = {'output_encoding': 'unicode', 'table_style': 'table'}
    return publish_string(text, writer=writer, writer_name='html5',
                          settings_overrides=settings)

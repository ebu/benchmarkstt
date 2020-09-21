"""
generate mermaid code that represent the inheritance of classes
defined in a given module, including some representation of class
members

Loosely ased on the code in:
https://github.com/mgaitan/sphinxcontrib-mermaid/blob/master/sphinxcontrib/autoclassdiag.py
https://github.com/mgaitan/sphinxcontrib-mermaid/blob/master/LICENSE.rst
"""
import inspect
from sphinx.util import import_object
from sphinxcontrib.mermaid import mermaid, figure_wrapper, align_spec
from docutils.parsers.rst import Directive, directives


def class_name(cls):
    """Return a string representing the class"""
    return cls.__name__.replace('.', '_')


class MagicTraits(object):
    MAGIC_MEMBERS = {
        "__iter__": "iterable",
        "__next__": "iterable",
        "__call__": "callable",
        "__enter__": "context",
        "__exit__": "context",
        "__lt__": "comparable",
        "__le__": "comparable",
        "__eq__": "comparable",
        "__ne__": "comparable",
        "__gt__": "comparable",
        "__ge__": "comparable",
        "__contains__": "contains",
        "__getitem__": "mapping",
        "__setitem__": "mapping",
        "__delitem__": "mapping",
        "__reversed__": "reversible",
        "__getattr__": "attributes",
        "__getattribute__": "attributes",
        "__len__": "len",
        "__subclasshook__": False,
        "__repr__": False,
        "__str__": False,
        "__getnewargs__": False,
    }

    @classmethod
    def unveil(cls, k, _=None):
        return cls.MAGIC_MEMBERS.get(k, None)


class ClassMembersDiagram(object):
    def __init__(self, module_path, base_module=None):

        self.module = import_object(module_path)
        self.base_module = base_module or self.module.__name__
        self.module_classes = set()
        self.inheritances = []
        self.associations = []
        self.class_members = {}
        self.namedtuples = []
        self._populate_tree()

    @staticmethod
    def members_predicate(member):
        return inspect.isfunction(member) or inspect.ismethod(member)

    def _inspect_members(self, cls):
        members = [member
                   for member in inspect.getmembers(cls, self.members_predicate)]
        members.sort()

        traits = set()

        def format_trait(name):
            return "<<%s>>" % (name,)

        def filter_self_and_cls(x):
            return x.name.lstrip('_') not in ['self', 'cls']

        def inspect_param(param):
            if (
                    inspect.isclass(param.annotation) and
                    cls.__module__.startswith(param.annotation.__module__.split('.', 2)[0]) and
                    class_name(param.annotation) != class_name(cls)
               ):
                self.associations.append("%s <.. %s" % (class_name(param.annotation), class_name(cls)))
                self._inspect_class(param.annotation, True)
                return ': '.join([param.name, param.annotation.__name__])
            return str(param)

        members_list = []
        init_args = []

        if tuple in cls.__bases__ and hasattr(cls, '_fields'):
            traits.add('namedtuple')

        for name, member in members:
            if name.startswith('_') and not (name.startswith('__') and name.endswith('__')):
                continue

            try:
                sig = inspect.signature(member)
            except ValueError:
                continue

            trait = MagicTraits.unveil(name)
            if trait is False:
                continue
            if trait is not None:
                traits.add(trait)
                continue

            params = list(sig.parameters.values())
            prefix = ''
            postfix = ''
            if len(params) != 0 and params[0].name != 'self':
                postfix = '$'
            else:
                prefix = '-' if name[0] == '_' else '+'
            params = filter(filter_self_and_cls, params)
            params = list(map(inspect_param, params))

            if name == '__init__':
                members_list.insert(0, '\n\t'.join(params))
                continue

            params_str = ', '.join(params)
            members_list.append(''.join([
                prefix,
                name,
                '(',
                params_str,
                ')',
                postfix
                ]))

        if inspect.isabstract(cls):
            traits.add('abstract')

        traits = list(map(format_trait, list(traits)))

        members_list.sort()
        traits.sort(key=len)

        self.class_members[class_name(cls)] = traits + \
                                              init_args + \
                                              members_list

    def _inspect_class(self, cls, force=False):
        if not inspect.isclass(cls):
            return

        cls_name = class_name(cls)
        if cls_name.startswith('_') or cls_name in self.module_classes:
            return

        if not cls.__module__.startswith(self.base_module) and not force:
            return

        if tuple in cls.__bases__ and hasattr(cls, '_fields'):
            self.namedtuples.append('\nclass %s {\n%s\n%s\n}' %
                                    (class_name(cls),
                                     "\t<<namedtuple>>",
                                     '\n\t'.join(cls._fields)
                                     ))
            return

        self._inspect_members(cls)

        self.module_classes.add(cls_name)
        for base in cls.__bases__:
            if class_name(base) == 'object' or class_name(base) == 'ABC':
                continue
            self.inheritances.append((class_name(base), cls_name))
            self._inspect_class(base)

    def _populate_tree(self):
        for obj in self.module.__dict__.values():
            self._inspect_class(obj)

    def _members_str(self):
        return [
            "\nclass %s {\n\t%s\n}" % (clsname.replace('.', ''), "\n\t".join(members))
            for clsname, members in self.class_members.items()
        ]

    def __str__(self):
        contents = "\n".join(
            list(self.module_classes) +
            [
                "%s <|-- %s" % (a, b)
                for a, b in self.inheritances if a != b
            ] +
            self.associations +
            self.namedtuples +
            self._members_str()
        )

        if not contents:
            return ""

        return "classDiagram\n" + contents


class MermaidClassMembersDiagram(Directive):
    """
    Directive to automagically add create an extended class diagram from python code.
    """
    has_content = False
    required_arguments = 1
    option_spec = {
        'alt': directives.unchanged,
        'align': align_spec,
        'caption': directives.unchanged,
    }

    def run(self):
        code = str(ClassMembersDiagram(*self.arguments, **self.options))
        if len(code) == 0:
            return []

        node = mermaid()
        node['code'] = "\n\n".join([
            "%%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#e7f2fa', 'lineColor': '#2980B9' }}}%%",
            code
        ])
        node['options'] = {}
        if 'alt' in self.options:
            node['alt'] = self.options['alt']
        if 'align' in self.options:
            node['align'] = self.options['align']
        if 'inline' in self.options:
            node['inline'] = True

        caption = self.options.get('caption')
        if caption:
            node = figure_wrapper(self, node, caption)

        return [node]

"""
generate mermaid code that represent the inheritance of classes
defined in a given module, including some representation of class
members

Based on the code in:
https://github.com/mgaitan/sphinxcontrib-mermaid/blob/master/sphinxcontrib/autoclassdiag.py
https://github.com/mgaitan/sphinxcontrib-mermaid/blob/master/LICENSE.rst
"""
from __future__ import print_function
import inspect
from sphinx.util import import_object
from sphinxcontrib.mermaid import Mermaid


def class_name(cls):
    """Return a string representing the class"""
    # NOTE: can be changed to str(class) for more complete class info
    return cls.__name__.replace('.', '_')


class MagicTraits(object):
    MAGIC_MEMBERS = {
        "__iter__": "Iterable",
        "__next__": "Iterable",
        "__call__": "Callable",
        "__enter__": "ContextManager",
        "__exit__": "ContextManager",
        "__lt__": "Comparable",
        "__le__": "Comparable",
        "__eq__": "Comparable",
        "__ne__": "Comparable",
        "__gt__": "Comparable",
        "__ge__": "Comparable",
        "__getitem__": "Indexable",
        "__reversed__": "Reversible",
        "__getattr__": "Attributes",
        "__getattribute__": "Attributes",
        "__repr__": None,
        "__str__": None,
    }

    @classmethod
    def unveil(cls, k, _=None):
        return cls.MAGIC_MEMBERS.get(k, False)


class ClassMembersDiagram(object):
    def __init__(self, module_path, base_module=None):

        self.module = import_object(module_path)
        self.base_module = base_module or self.module.__name__
        self.module_classes = set()
        self.inheritances = []
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
            return "<<%s>>\n" % (name,)

        def filter_self_and_cls(x):
            nonlocal prefix
            if x.name == 'cls':
                prefix = '$'
            return x.name not in ['self', 'cls']

        members_list = []
        init_args = []

        if tuple in cls.__bases__ and hasattr(cls, '_fields'):
            traits.add('namedtuple')

        for name, member in members:
            try:
                sig = inspect.signature(member)
            except ValueError:
                continue

            prefix = None
            params = filter(filter_self_and_cls, sig.parameters.values())
            sig = sig.replace(parameters=params)
            params = sig.parameters.values()

            if name == '__init__':
                init_args = list(map(str, list(params)))
                continue

            trait = MagicTraits.unveil(name)
            if trait:
                traits.add(trait)
                continue

            if prefix is None:
                prefix = '-' if name[0] == '_' else '+'

            members_list.append(''.join([prefix, name, str(sig)]))

        traits = list(map(format_trait, list(traits)))
        self.class_members[class_name(cls)] = traits + \
                                              init_args + \
                                              members_list

    def _inspect_class(self, cls):
        if not inspect.isclass(cls):
            return

        cls_name = class_name(cls)
        if cls_name in self.module_classes:
            return

        if not cls.__module__.startswith(self.base_module):
            return

        if tuple in cls.__bases__ and hasattr(cls, '_fields'):
            self.namedtuples.append('class %s {\n<<namedtuple>>\n%s\n}' %
                                    (class_name(cls), "\n".join(cls._fields)))
            return

        self._inspect_members(cls)

        self.module_classes.add(cls_name)
        for base in cls.__bases__:
            if class_name(base) == 'object':
                continue
            self.inheritances.append((class_name(base), cls_name))
            self._inspect_class(base)

    def _populate_tree(self):
        for obj in self.module.__dict__.values():
            self._inspect_class(obj)

    def _members_str(self):
        return [
            "class %s {\n\t%s\n}" % (clsname.replace('.', ''), "\n\t".join(members))
            for clsname, members in self.class_members.items()
        ]

    def __str__(self):
        m = self._members_str()
        return "classDiagram\n" + "\n".join(
            list(self.module_classes) + [
                "%s <|-- %s" % (a, b)
                for a, b in self.inheritances
            ] +
            self.namedtuples +
            m
        )


class MermaidClassMembersDiagram(Mermaid):
    option_spec = {
        'test': bool,
    }

    has_content = False
    required_arguments = 1

    def get_mm_code(self):
        return u'{}'.format(ClassMembersDiagram(*self.arguments, **self.options))


if __name__ == "__main__":
    print(ClassMembersDiagram('sphinx.util'))

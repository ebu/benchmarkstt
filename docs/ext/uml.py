"""
Module used to generate PlantUML class diagrams for benchmarkstt.

Currently only used for documentation purposes.

Warning:
    Code is made to purpose, untested and unused in actual benchmarkstt.
    As such, this code could use a cleanup and some decent architecture.
    Currently though, meh... -MikeSmithEU

"""


import inspect
import pkgutil
import os
import logging
import sys


from importlib import import_module
from pathlib import Path

logger = logging.getLogger('benchmarksttdocs.uml')


class PlantUMLBlock:
    start_block = "%s {"
    end_block = "}"

    def __init__(self, uml, block_text=None):
        self._uml = uml
        self._block_text = block_text

    def __enter__(self):
        if self._block_text:
            self._uml.add(self.start_block, self._block_text)
        self._uml.level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._uml.level -= 1
        if self._block_text:
            self._uml.add(self.end_block,)
        self._uml.add()


class Package:
    def __init__(self, uml, module, filter_=None):
        if not inspect.ismodule(module):
            raise Exception("Expected a module")

        classes = [(name, cls)
                   for name, cls in inspect.getmembers(module, predicate=inspect.isclass)
                   if filter_ and filter_(cls)]

        if not classes:
            return

        with PlantUMLBlock(uml, "package %s %s" % (module.__name__, uml.link(module.__name__))):
            for name, cls in classes:
                uml.klass(cls)


class FunctionTests:
    MAGIC_DUCKS = {
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
    def is_protected(cls, k, _=None):
        return k.startswith('_') and not cls.is_magic(k)

    @staticmethod
    def is_magic(k, _=None):
        return k.startswith('__') and k.endswith('__')

    @staticmethod
    def contains(k, options=None):
        return options and k in options

    @classmethod
    def is_magic_duck(cls, k, _=None):
        return cls.magic_to_duck(k) is not False

    @classmethod
    def magic_to_duck(cls, k, _=None):
        return cls.MAGIC_DUCKS.get(k, False)


class KlassTests:
    @staticmethod
    def is_exception(klass):
        return issubclass(klass, BaseException)

    @staticmethod
    def is_namedtuple(klass):
        return tuple in klass.__bases__ and hasattr(klass, '_fields')


class Klass:
    def __init__(self, uml, klass, **kwargs):
        self._uml = uml
        self._klass = klass
        self._options = kwargs

        if KlassTests.is_namedtuple(klass):
            self.namedtuple()
        else:
            self.klass()
        self.stop()

    def _classlink(self):
        return self._uml.link(
            self._klass.__module__,
            self._klass.__module__ + '.' + self._klass.__name__
        )

    def namedtuple(self):
        self._uml.add()
        self._uml.add(
            'class %s<namedtuple> << (T, yellow) >> %s {',
            self._uml.cls_name(self._klass),
            self._classlink()
        )
        self._uml.level += 1
        self._uml.add('.. Fields ..')

        for field in self._klass._fields:
            self._uml.add("+%s", field)

    def klass(self):
        def methods_filter(member):
            if inspect.isfunction(member) or inspect.ismethod(member):
                return member.__module__.startswith('benchmarkstt.')
            return False
        self._uml.add()

        extends = ''
        outside_extends = ''
        bases = [[], []]

        def join(classes):
            return ', '.join(map(self._uml.cls_name, classes)),

        for cls in self._klass.__bases__:
            bases[self._uml.filtered(cls)].append(cls)

        if len(bases[0]):
            extends = 'extends %s ' % join(bases[0])

        bases[1] = list(filter(lambda cls: cls.__module__.startswith('benchmarkstt.'), bases[1]))
        if len(bases[1]):
            outside_extends = '<extends %s>' % join(bases[1])

        meta = ''
        if KlassTests.is_exception(self._klass):
            meta = '<< (E,red) >>'

        members = inspect.getmembers(self._klass, predicate=methods_filter)
        members.sort()

        magic_ducks = sorted(set(filter(None, map(FunctionTests.magic_to_duck, map(lambda x: x[0], members)))))
        magic_ducks = '<< {} >>'.format(" >> << ".join(magic_ducks)) if magic_ducks else ''

        self._uml.add(
            'class %s.%s%s %s %s %s %s{',
            self._klass.__module__,
            self._klass.__name__,
            outside_extends,
            magic_ducks,
            meta,
            self._classlink(),
            extends
        )
        self._uml.level += 1

        skippables = {
            'skip_protected': FunctionTests.is_protected,
            'skip_magic': FunctionTests.is_magic,
            'skip': FunctionTests.contains,
        }

        def should_skip(k):
            return FunctionTests.is_magic_duck(k) or any(
                (
                    self._options.get(option_name) and func(k, self._options.get(option_name))
                    for option_name, func in skippables.items()
                )
            )

        def format_signature(sig):
            def filter_self_and_cls(x):
                return x.name not in ['self', 'cls']
            params = filter(filter_self_and_cls, sig.parameters.values())
            return str(sig.replace(parameters=params))

        contents = {
            "public": [],
            "protected": [],
            "static": [],
        }

        for k, member in members:
            if should_skip(k):
                continue
            kind = 'protected' if FunctionTests.is_protected(k) else 'public'

            fmt = '%s%s%s'
            extra = ''

            if inspect.isbuiltin(member):
                continue

            if inspect.ismethoddescriptor(member):
                continue

            if inspect.ismethod(member):
                fmt = '{static} ' + fmt
                kind = 'static'

            extra = format_signature(inspect.signature(getattr(self._klass, k)))
            contents[kind].append((fmt, k, extra))

        for kind in ("public", "protected", "static"):
            if not len(contents[kind]):
                continue

            self._uml.add(".. %s Methods ..", kind.capitalize())

            icon = '#' if kind == 'protected' else '+'
            for fmt, k, extra in contents[kind]:
                self._uml.add(fmt, icon, k, extra)

        return self

    def stop(self):
        self._uml.level -= 1
        self._uml.add('}')


class PlantUML:
    def __init__(self, filter=None, link_tpl=None):
        self.parent_arrow = '-up-|>'
        self.classes_done = set()
        self._buffer = ""
        self._relations = []
        self.level = 0
        self._filter = filter
        self._link_tpl = link_tpl

    def skinparam(self, value):
        self.add("skinparam %s", value)

    def includeurl(self, url):
        self.add("!includeurl %s", url)

    def link(self, page, hash_=None, is_field_or_method=None):
        if self._link_tpl is None:
            return ''

        if hash_ is None:
            hash_ = ''

        tpl = '[[[%s]]]' if is_field_or_method else '[[%s]]'
        link = self._link_tpl.format(page=page, hash=hash_)
        if not link:
            return ''
        return tpl % (link,)

    def add(self, what=None, *args):
        if what is None:
            self._buffer += "\n"
            return
        self._buffer += "\t" * self.level
        self._buffer += what % tuple(args) if len(args) else what
        self._buffer += "\n"

    def title(self, title):
        self.add("title %s", title)
        self.add()

    def direction(self, which):
        self.add("%s direction", which)

    def generate(self, orig_module):
        def filter_protected(v):
            return not v.startswith('_')

        path = str(os.path.dirname(os.path.realpath(orig_module.__file__)))

        for f in Path(path).rglob("*.py"):
            module = list(filter(filter_protected, str(f)[len(path)+1:-3].split(os.path.sep)))
            module_name = '%s.%s' % (orig_module.__name__, '.'.join(module),) if len(module) else orig_module.__name__
            module = import_module(module_name)
            self.package(module)

        return str(self)

    @staticmethod
    def cls_name(cls):
        return '.'.join((cls.__module__, cls.__name__))

    def class_filter(self, cls):
        if self.filtered(cls):
            return False
        if cls in self.classes_done:
            return False
        self.classes_done.add(cls)
        return True

    def filtered(self, cls):
        return False if self._filter is None else self._filter(cls)

    def package(self, module):
        return Package(self, module, filter_=self.class_filter)

    def parent_relations(self, cls):
        for parent_cls in cls.__bases__:
            if not self.filtered(parent_cls):
                self.relation(cls, self.parent_arrow, parent_cls)

    def relation(self, a, arrow, b):
        self._relations.append(" ".join((self.cls_name(a), arrow, self.cls_name(b))))
        return self

    def klass(self, klass):
        return Klass(self, klass)

    def __str__(self):
        return "\n".join(
            (
                "@startuml\n",
                self._buffer,
                "\n".join(self._relations),
                "\n@enduml",
            )
        )


def generate(package_dir, output_dir='./_static/autogen/'):
    """
    Generates basic PlantUML schemas for benchmarkstt
    """

    file_tpl = os.path.join(output_dir, '%s.%s')
    link_tpl = "https://benchmarkstt.readthedocs.io/en/latest/modules/{page}.html#{hash}"

    def benchmarkstt_filter(cls):
        return not cls.__qualname__.startswith('benchmarkstt.')

    def benchmarkstt_filter_for(name):
        def _filter(cls):
            return benchmarkstt_filter(cls) and \
                   not (hasattr(cls, '__module__') and cls.__module__.startswith('benchmarkstt.%s' % (name,)))

        return _filter

    def generate(package, filter_, direction=None):
        name = package.__name__
        uml = PlantUML(filter=filter_, link_tpl=link_tpl)
        if direction:
            uml.direction(direction)

        uml.skinparam('packageStyle Frame')

        generated = uml.generate(package)
        file_name = file_tpl % (name, 'puml')
        with open(file_name, 'w') as f:
            f.write(generated)
        return file_name

    import benchmarkstt
    packages = [name
                for _, name, ispkg in pkgutil.iter_modules([package_dir])
                if ispkg]

    for name in packages:
        full_name = "benchmarkstt.%s" % (name,)
        logger.info("Generating UML for %s", name)
        package = import_module(full_name)
        generate(package, benchmarkstt_filter_for(name))

    logger.info("Generating UML for complete package")
    generate(benchmarkstt, benchmarkstt_filter_for(''))

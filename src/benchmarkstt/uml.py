import inspect
import pkgutil
import os

from pathlib import Path
from contextlib import nullcontext


class PlantUMLBlock:
    start_block = "%s {"
    end_block = "}"

    def __init__(self, uml, block_text=None):
        self._uml = uml
        self._block_text = block_text

    def __enter__(self):
        self._uml.level += 1
        if self._block_text:
            self._uml.add(self.start_block, self._block_text)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._block_text:
            self._uml.add(self.end_block,)
        self._uml.level -= 1


class Namespace(PlantUMLBlock):
    def __init__(self, uml, name):
        block_text = "namespace %s" % (name,)
        super().__init__(uml, block_text)

    def __enter__(self):
        super().__enter__()
        return self


class Module(PlantUMLBlock):
    def __init__(self, uml, module):
        self._module = module
        super().__init__(uml)

    def __enter__(self):
        super().__enter__()

        for name, cls in inspect.getmembers(self._module, predicate=inspect.isclass):
            with self._uml.klass(self._uml.cls_name(cls), cls):
                pass
        return self


class Klass(PlantUMLBlock):
    def __init__(self, uml, name, klass):
        self._name = name
        self._klass = klass
        super().__init__(uml, "class %s" % (name,))
        self._uml.parent_relations(self._klass)

    def method(self, required_args, optional_args):
        args = required_args + list(map(lambda x: '[%s]' % x, optional_args))
        self._uml.add("+__init__(%s)", ",".join(args))

    def __enter__(self):
        super().__enter__()

        todos = inspect.getmembers(self._klass, predicate=inspect.isfunction)
        todos.sort()
        for k, func in todos:
            if k.startswith('_') and not k.startswith('__'):
                continue

            signature = inspect.signature(getattr(self._klass, k))
            self._uml.add("\t+%s%s", k, signature)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)


class PlantUML:
    def __init__(self, filter=None):
        self.parent_arrow = '--up--|>'
        self.classes_done = set()
        self._buffer = ""
        self._relations = []
        self.level = 0
        self._filter = filter

    def add(self, what, *args):
        self += "\t" * self.level
        self += what % tuple(args) if len(args) else what
        self += "\n"

    def title(self, title):
        self.add("title %r", title)

    def direction(self, which):
        self.add("%s direction", which)

    def generate(self, orig_module):
        def filterProtected(v):
            return not v.startswith('__')

        def get_module(module, ctx=orig_module):
            try:
                current = module.pop(0)
            except IndexError:
                return ctx
            ctx = getattr(ctx, current)
            return get_module(module, ctx) if len(module) else ctx

        path = str(os.path.dirname(os.path.realpath(orig_module.__file__)))

        modules = {}
        for f in Path(path).rglob("*.py"):
            module = list(filter(filterProtected, str(f)[len(path)+1:-3].split(os.path.sep)))
            if len(module) == 0:
                continue
            module_name = '%s.%s' % (orig_module.__name__, '.'.join(module),)
            __import__(module_name)
            modules[module_name] = get_module(module)

        for module in modules.values():
            with self.module(module):
                pass

        return str(self)

    @staticmethod
    def cls_name(cls):
        return '.'.join((cls.__module__, cls.__name__))

    def render(self, orig_module, format='svg'):
        from plantweb.render import render
        return render(
            self.generate(orig_module),
            engine='plantuml',
            format=format,
            cacheopts={
                'use_cache': False
            }
        )[0]

    def skip(self, cls):
        if self.filtered(cls):
            return True
        if cls in self.classes_done:
            return True
        self.classes_done.add(cls)
        return False

    def filtered(self, cls):
        return False if self._filter is None else self._filter(cls)

    def __add__(self, x):
        self._buffer += str(x)
        return self

    def module(self, module):
        return Module(self, module)

    def parent_relations(self, cls):
        if not self.skip(cls):
            return
        for parent_cls in cls.__bases__:
            if not self.filtered(parent_cls):
                self.relation(cls, self.parent_arrow, parent_cls)

    def relation(self, a, arrow, b):
        self._relations.append(" ".join((self.cls_name(a), arrow, self.cls_name(b))))
        return self

    def namespace(self, name):
        return Namespace(self, name)

    def klass(self, name, klass):
        if self.skip(klass):
            return nullcontext()
        return Klass(self, name, klass)

    def entity(self, entity, conf=None):
        return Entity(self, entity, conf)

    def __str__(self):
        return "\n".join(
            (
                "@startuml",
                self._buffer,
                "\n".join(self._relations),
                "@enduml",
            )
        )


if __name__ == '__main__':
    # generate basic PlantUML schemas for benchmarkstt
    file_tpl = './docs/_static/uml/%s.%s'
    files = {}
    extensions = ('plantuml', 'svg')
    for extension in extensions:
        files[extension] = file_tpl % ('benchmarkstt', extension)

    def benchmarksttFilterFor(name):
        module_name = 'benchmarkstt.%s' % (name,)

        def benchmarksttFilter(cls):
            if cls.__name__.startswith(module_name):
                return False

            if hasattr(cls, '__module__') and cls.__module__.startswith(module_name):
                return False

            return True
        return benchmarksttFilter

    def generate(name, module, filter, direction=None):
        title = name.capitalize()
        uml = PlantUML(filter=filter)
        if direction:
            uml.direction(direction)
        uml.title(title)
        files = {
                    extension: file_tpl % (name, extension) for extension in extensions
                }

        with open(files['plantuml'], 'w') as f:
            f.write(uml.generate(module))
        with open(files['svg'], 'wb') as f:
            f.write(uml.render(module))

    import benchmarkstt
    modules = [name for _, name, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)]) if ispkg]

    for name in modules:
        print("Generating UML for %s" % (name,))
        module = __import__("benchmarkstt.%s" % (name,))
        generate(name, module, benchmarksttFilterFor(name))

    print("Generating UML for complete package\n")
    generate('benchmarkstt', benchmarkstt, benchmarksttFilterFor(''), "left to right")

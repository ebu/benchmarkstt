import inspect
import pkgutil
import os
import subprocess
from importlib import import_module
import logging

from pathlib import Path
from contextlib import nullcontext

logger = logging.getLogger(__name__)


class PlantUMLWebRenderer:
    def __init__(self, format=None):
        if format is None:
            format = 'svg'
        self._format = format

    def render(self, data):
        from plantweb.render import render
        return render(
            data,
            engine='plantuml',
            format=self._format,
            cacheopts={
                'use_cache': False
            }
        )[0]


class PlantUMLJarRenderer:
    """
    Note: requires PlantUML from https://plantuml.com/download
    """

    DEFAULT_COMMAND = os.environ.get("PLANTUML", "java -jar plantuml.jar").split(' ')
    DEFAULT_FORMAT = 'png'
    DEFAULT_TIMEOUT = 10

    def __init__(self, format=None, command=None, timeout=30):
        if command is None:
            command = self.DEFAULT_COMMAND
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        if format is None:
            format = self.DEFAULT_FORMAT

        self._process = None
        self._command = command
        self._timeout = timeout
        self._format = format

    def __process(self, *args):
        command = [*self._command, "-p", "-t%s" % (self._format), *args]
        return subprocess.Popen(command, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def render(self, data):
        proc = self.__process()

        if type(data) is str:
            data = data.encode()

        try:
            out, errs = proc.communicate(data, timeout=10)
            return out
        except subprocess.TimeoutExpired as e:
            proc.kill()
            self._process = None
            raise e


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
            with self._uml.klass(cls):
                pass
        return self


class Klass(PlantUMLBlock):
    def __init__(self, uml, klass):
        self._klass = klass
        logger.debug("Class: %s\tModule: %s" % (klass.__name__, klass.__module__))

        link = uml.link(klass.__module__, klass.__module__ + '.' + klass.__name__)
        super().__init__(uml, "class %s.%s %s" % (klass.__module__, klass.__name__, link))
        self._uml.parent_relations(self._klass)

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
    def __init__(self, filter=None, link_tpl=None):
        self.parent_arrow = '--up--|>'
        self.classes_done = set()
        self._buffer = ""
        self._relations = []
        self.level = 0
        self._filter = filter
        self._link_tpl = link_tpl

    def link(self, page, hash_, is_field_or_method=None):
        if self._link_tpl is None:
            return ''

        level = 3 if is_field_or_method else 2
        link = self._link_tpl.format(page=page, hash=hash_)
        if not link:
            return ''
        return ("[" * level) + link + ("]" * level)

    def add(self, what, *args):
        self += "\t" * self.level
        self += what % tuple(args) if len(args) else what
        self += "\n"

    def title(self, title):
        self.add("title %s", title)

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
        for parent_cls in cls.__bases__:
            if not self.filtered(parent_cls):
                self.relation(cls, self.parent_arrow, parent_cls)

    def relation(self, a, arrow, b):
        self._relations.append(" ".join((self.cls_name(a), arrow, self.cls_name(b))))
        return self

    def namespace(self, name):
        return Namespace(self, name)

    def klass(self, klass):
        if self.skip(klass):
            return nullcontext()
        return Klass(self, klass)

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
    import sys
    args = sys.argv[1:]

    logLevel = logging.INFO

    if '--verbose' in args:
        logLevel = logging.DEBUG
        del args[args.index('--verbose')]
    logging.basicConfig(level=logLevel)

    if '--help' in args:
        print("Usage: %s [--verbose] [--help] [filter1 [filter2 [filterN...]]]" % (sys.argv[0],))
        print()
        print("\t--verbose\tOutput all debug info")
        print("\t--help\tShow this usage message")
        print("\tfilterN\tNames of the uml packages we wish to generate (all if no arguments are present)")
        print()
        exit()

    # alternatively use PlantUMLWebRenderer or PlantUMLJarRenderer
    Renderer = PlantUMLJarRenderer

    file_tpl = './docs/_static/uml/%s.%s'
    plant_extensions = ('svg',)
    extensions = ('plantuml',) + plant_extensions  # , 'png')
    link_tpl = "https://benchmarkstt.readthedocs.io/en/latest/modules/{page}.html#{hash}"

    def benchmarkstt_filter_for(name):
        module_name = 'benchmarkstt.%s' % (name,)

        def benchmarkstt_filter(cls):
            if cls.__name__.startswith('benchmarkstt.'):
                return False

            if cls.__name__.startswith(module_name):
                return False

            if hasattr(cls, '__module__') and cls.__module__.startswith(module_name):
                return False

            return True

        def fil(cls):
            filtered = benchmarkstt_filter(cls)
            logger.debug("FILTER: %s\t%s ", "SKIPPED" if filtered else "OK", cls)
            return filtered

        return fil  # benchmarkstt_filter

    renderers = {ext: Renderer(format=ext) for ext in plant_extensions}

    def generate(package, filter_, direction=None):
        name = package.__name__
        title = name.capitalize()
        uml = PlantUML(filter=filter_, link_tpl=link_tpl)
        if direction:
            uml.direction(direction)
        uml.title(title)
        files = {
                    extension: file_tpl % (name, extension) for extension in extensions
                }

        generated = uml.generate(package)
        with open(files['plantuml'], 'w') as f:
            f.write(generated)

        for ext in plant_extensions:
            with open(files[ext], 'wb') as f:
                f.write(renderers[ext].render(generated))

    import benchmarkstt
    packages = [name
                for _, name, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)])
                if ispkg and name != 'benchmark']

    for name in packages:
        if len(args) and name not in args:
            logger.info("SKIPPED Generating UML for %s" % (name,))
            continue
        full_name = "benchmarkstt.%s" % (name,)
        logger.info("Generating UML for %s" % (name,))
        package = import_module(full_name)
        generate(package, benchmarkstt_filter_for(name))

    if len(args) == 0 or 'benchmarkstt' in args:
        renderers = {ext: Renderer(format=ext) for ext in plant_extensions}
        logger.info("Generating UML for complete package")
        generate(benchmarkstt, benchmarkstt_filter_for(''), "left to right")
    else:
        logger.info("SKIPPED Generating UML for complete package")

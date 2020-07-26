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
    Note: requires PlantUML's `plantuml.jar` from https://plantuml.com/download
    """

    DEFAULT_COMMAND = os.environ.get("PLANTUML", "java -jar plantuml.jar").split(' ')
    DEFAULT_FORMAT = 'svg'
    DEFAULT_TIMEOUT = 10

    def __init__(self, format=None, command=None, timeout=None):
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
        if self._block_text:
            self._uml.add(self.start_block, self._block_text)
        self._uml.level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._uml.level -= 1
        if self._block_text:
            self._uml.add(self.end_block,)
        self._uml.add()


class Namespace(PlantUMLBlock):
    def __init__(self, uml, name):
        block_text = "namespace %s" % (name,)
        super().__init__(uml, block_text)


class Package:
    def __init__(self, uml, module):
        if not inspect.ismodule(module):
            raise Exception("Expected a module")

        with PlantUMLBlock(uml, "package %s" % (module.__name__,)):
            for name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                uml.klass(cls)
                uml.add()


class KlassTests:
    @classmethod
    def is_protected(cls, k, _=None):
        return k.startswith('_') and not cls.is_magic(k)

    @staticmethod
    def is_magic(k, _=None):
        return k.startswith('__') and k.endswith('__')

    @staticmethod
    def contains(k, options=None):
        return options and k in options

    @staticmethod
    def is_namedtuple(klass):
        return tuple in klass.__bases__ and hasattr(klass, '_fields')


class Klass:
    def __init__(self, uml, klass, **kwargs):
        self._uml = uml
        self._klass = klass
        self._options = kwargs

        # uml.parent_relations(self._klass)
        if KlassTests.is_namedtuple(klass):
            self.tuple()
        else:
            self.start()
            self.methods()
        self.stop()

    def _classlink(self):
        return self._uml.link(
            self._klass.__module__,
            self._klass.__module__ + '.' + self._klass.__name__
        )

    def start(self):
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
        if cls.__name__.endswith('Error'):
            meta = '<< (E,red) >>'

        self._uml.add(
            'class %s.%s%s %s %s %s{',
            self._klass.__module__,
            self._klass.__name__,
            outside_extends,
            meta,
            self._classlink(),
            extends
        )
        self._uml.level += 1

    def tuple(self):
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

    def methods(self):
        members = inspect.getmembers(self._klass, predicate=inspect.isroutine)
        members.sort()

        skippables = {
            'skip_protected': KlassTests.is_protected,
            'skip_magic': KlassTests.is_magic,
            'skip': KlassTests.contains,
        }

        def should_skip(k):
            return any(
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
            kind = 'protected' if KlassTests.is_protected(k) else 'public'

            fmt = '%s%s%s'
            extra = ''

            if inspect.isbuiltin(member):
                continue

            if inspect.ismethoddescriptor(member):
                continue

            if inspect.ismethod(member):
                fmt = '{static} ' + fmt
                extra = format_signature(inspect.signature(getattr(self._klass, k)))
                kind = 'static'
            elif inspect.isfunction(member):
                extra = format_signature(inspect.signature(getattr(self._klass, k)))
            else:
                logger.debug('UNKNOWN TYPE skip: %s %s', k, member)
                continue
            contents[kind].append((fmt, k, extra))

        for kind in ("public", "protected", "static"):
            if not len(contents[kind]):
                continue

            self._uml.add(".. %s Methods ..", kind.capitalize())

            icon = '-' if kind == 'protected' else '+'
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

    def link(self, page, hash_, is_field_or_method=None):
        if self._link_tpl is None:
            return ''

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

    def skip(self, cls):
        if self.filtered(cls):
            return True
        if cls in self.classes_done:
            return True
        self.classes_done.add(cls)
        return False

    def filtered(self, cls):
        return False if self._filter is None else self._filter(cls)

    def package(self, module):
        return Package(self, module)

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
                "@startuml\n",
                self._buffer,
                "\n".join(self._relations),
                "\n@enduml",
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

    # support colored logs if installed
    try:
        import coloredlogs
        coloredlogs.install(level=logLevel)
    except ImportError:
        pass

    logging.basicConfig(level=logLevel)

    if '--help' in args:
        print("Usage: %s [--verbose] [--help] [filter1 [filter2 [filterN...]]]" % (sys.argv[0],))
        print()
        print("\t--verbose\tOutput all debug info")
        print("\t--help\tShow this usage message")
        print("\tfilterN\tNames of the packages for which we wish to generate UML (all if no arguments are present)")
        print()
        exit()

    # alternatively use PlantUMLWebRenderer or PlantUMLJarRenderer
    Renderer = PlantUMLJarRenderer

    file_tpl = './docs/_static/uml/%s.%s'
    extensions = ('puml', 'svg')
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

    svg_renderer = Renderer(format='svg')

    def generate(package, filter_, direction=None):
        name = package.__name__
        title = name
        uml = PlantUML(filter=filter_, link_tpl=link_tpl)
        if direction:
            uml.direction(direction)
        uml.title(title)
        uml.skinparam('packageStyle Frame')

        # decrease ugliness
        uml.add('!define LIGHTORANGE')
        uml.includeurl('https://raw.githubusercontent.com/Drakemor/RedDress-PlantUML/master/style.puml')

        generated = uml.generate(package)
        with open(file_tpl % (name, 'puml'), 'w') as f:
            f.write(generated)

        with open(file_tpl % (name, 'svg'), 'wb') as f:
            f.write(svg_renderer.render(generated))

    import benchmarkstt
    packages = [name
                for _, name, ispkg in pkgutil.iter_modules([os.path.dirname(__file__)])
                if ispkg and name != 'benchmark']

    for name in packages:
        if len(args) and name not in args:
            logger.debug("SKIPPED Generating UML for %s", name)
            continue
        full_name = "benchmarkstt.%s" % (name,)
        logger.info("Generating UML for %s", name)
        package = import_module(full_name)
        generate(package, benchmarkstt_filter_for(name))

    if len(args) == 0 or 'benchmarkstt' in args:
        logger.info("Generating UML for complete package")
        generate(benchmarkstt, benchmarkstt_filter_for(''), "left to right")
    else:
        logger.debug("SKIPPED Generating UML for complete package")

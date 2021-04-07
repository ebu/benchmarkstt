import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported')


def from_file(filename):
    with open(filename) as f:
        result = f.read()
    return result.strip()

def filter_requirements(line):
    return not line.startswith('-e')

docs_require = list(filter(filter_requirements, from_file('docs/requirements.txt').split('\n')))

dirname = os.path.dirname(__file__)
__version__ = from_file('VERSION')
__author__ = 'EBU'
__name__ = 'benchmarkstt'

# Auto save to __meta__
meta_location = os.path.join(dirname, 'src', __name__, '__meta__.py')
with open(meta_location, 'w') as f:
    f.write('''# Automatically created. DO NOT EDIT
__version__ = %s
__author__ = %s
''' % (repr(__version__), repr(__author__)))

long_description = from_file('README.rst')

setup(
    name=__name__,
    url='https://github.com/ebu/benchmarkstt/',
    license='MIT',
    version=__version__,
    author=__author__,
    author_email='ai-stt@list.ebu.ch',
    maintainer=__author__,
    maintainer_email='ai-stt@list.ebu.ch',
    description='A library for benchmarking AI/ML applications.',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.5',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'benchmarkstt': ['api/templates/*.html']},
    include_package_data=True,
    install_requires=[
        'MarkupSafe>=1.0',
        'Flask>=1.0.2',
        'jsonrpcserver>=4.0.1',
        'gunicorn>=19.9.0',
        'docutils>=0.14',
        'editdistance>=0.5.3',
        'Unidecode>=1.1.2',
    ],
    extras_require={
        'test': [
            "pytest==4.2.0",
            "pycodestyle==2.5.0",
            "pytest-cov==2.5.1",
            "attrs==19.1.0",
        ],
        'docs': docs_require,
    },
    platforms='any',
    entry_points={
        'console_scripts': [
            "%s=%s.cli.main:run" % (__name__, __name__),
            "%s-tools=%s.cli.tools:run" % (__name__, __name__)
        ],
    }
)

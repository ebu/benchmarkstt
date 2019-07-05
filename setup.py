import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3, 5):
    sys.exit('Sorry, Python < 3.5 is not supported')

dirname = os.path.dirname(__file__)
with open('VERSION') as f:
    __version__ = f.read().strip()
__author__ = 'EBU'
__name__ = 'benchmarkstt'

# Auto save to __meta__
meta_location = os.path.join(dirname, 'src', __name__, '__meta__.py')
with open(meta_location, 'w') as f:
    f.write('''# Automatically created. DO NOT EDIT
__version__ = %s
__author__ = %s
''' % (repr(__version__), repr(__author__)))

with open('README.rst') as f:
    long_description = f.read()


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
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.5',
    packages=find_packages("src"),
    package_dir={"": "src"},
    package_data={'benchmarkstt': ['api/templates/*.html']},
    include_package_data=True,
    install_requires=[
        'MarkupSafe>=1.0',
        'Unidecode>=1.0.22',
        'langcodes>=1.4.1',
        'Flask>=1.0.2',
        'jsonrpcserver>=4.0.1',
        'gunicorn>=19.9.0',
        'docutils>=0.14',
    ],
    extras_require={
        'docs': [
            "sphinx==1.8.3",
            "sphinx_rtd_theme==0.4.2",
            "sphinx-argparse==0.2.5",
        ],
        'test': [
            "pytest==4.2.0",
            "pycodestyle==2.5.0",
            "pytest-cov==2.5.1"
        ]
    },
    platforms='any',
    entry_points={
        'console_scripts': [
            "%s=%s.cli:main" % (__name__, __name__),
            "%s-tools=%s.cli:tools" % (__name__, __name__)
        ],
    }
)

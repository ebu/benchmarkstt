import os

from setuptools import setup, find_packages

dirname = os.path.dirname(__file__)
__version__ = open('VERSION').read().strip()
__author__ = 'EBU'
# had to call it something...
__name__ = 'conferatur'

# Auto save to __meta__
meta_location = os.path.join(dirname, 'src', __name__, '__meta__.py')
open(meta_location, 'wb').write('''# Automagically created. DO NOT EDIT
__version__ = '%s'
__author__ = '%s'
''' % (__version__, __author__))

setup(
    name=__name__,
    url='https://github.com/ebu/ai-benchmarking-stt/',
    version=__version__,
    author=__author__,
    author_email='',
    description='',
    long_description=open('README.md').read(),
    classifiers=[
        'Programming Language :: Python',
    ],
    package_dir={'': 'conferatur'},
    packages=('conferatur',),
    install_requires=[
        'unidecode',
        'langcodes',
    ],
    extras_require={
        'dev': [
            'doctest',
        ],
    },
    platforms='any',
)

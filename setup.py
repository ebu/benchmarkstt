import os

from setuptools import setup

dirname = os.path.dirname(__file__)
with open('VERSION') as f:
    __version__ = f.read().strip()
__author__ = 'EBU'
# had to call it something...
__name__ = 'conferatur'

# Auto save to __meta__
meta_location = os.path.join(dirname, 'src', __name__, '__meta__.py')
with open(meta_location, 'wb') as f:
    f.write('''# Automagically created. DO NOT EDIT
__version__ = '%s'
__author__ = '%s'
''' % (__version__, __author__))

with open('README.md') as f:
    long_description = f.read()

setup(
    name=__name__,
    url='https://github.com/ebu/ai-benchmarking-stt/',
    version=__version__,
    author=__author__,
    author_email='',
    description='',
    long_description=long_description,
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

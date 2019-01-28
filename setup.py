import os

from setuptools import setup

dirname = os.path.dirname(__file__)
with open('VERSION') as f:
    __version__ = f.read().strip()
__author__ = 'EBU'
# had to call it something...
__name__ = 'conferatur'

# Auto save to __meta__
meta_location = os.path.join(dirname,  __name__, '__meta__.py')
with open(meta_location, 'w') as f:
    f.write('''# Automagically created. DO NOT EDIT
__version__ = %s
__author__ = %s
''' % (repr(__version__), repr(__author__)))

with open('README.md') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    install_requires = f.readlines()

with open('requirements-docs.txt') as f:
    docs_requirements = f.readlines()

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
    packages=('conferatur',),
    install_requires=install_requires,
    extras_require={
        'docs': docs_requirements,
    },
    platforms='any',
    entry_points={
        "console_scripts": [
            "%s=cli.py" % (__name__,)
        ],
    }
)

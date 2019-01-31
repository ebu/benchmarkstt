import os
import sys
from setuptools import setup, find_packages

if sys.version_info < (3,4):
    sys.exit('Sorry, Python < 3.4 is not supported')

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


setup(
    name=__name__,
    url='https://github.com/ebu/ai-benchmarking-stt/',
    version=__version__,
    author=__author__,
    author_email='temp@example.com',
    description='',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.4',
    packages=find_packages(),
    install_requires=[
       'Unidecode>=1.0.22',
       'langcodes>=1.4.1'
    ],
    platforms='any',
    entry_points={
        'console_scripts': [
            "%s=%s.cli:main" % (__name__, __name__)
        ],
    }
)

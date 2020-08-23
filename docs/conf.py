import os
import sys
from datetime import datetime
from sphinx.ext.apidoc import main as sphinx_apidoc
from benchmarkstt.api.jsonrpc import get_methods
from benchmarkstt.docblock import format_docs

# Configuration file for the Sphinx documentation builder.
# see the documentation: http://www.sphinx-doc.org/en/master/config


description = 'A library for benchmarking AI/ML applications.'
project = 'BenchmarkSTT'
author = 'EBU'
copyright = '2019-%d, %s' % (datetime.now().year, author)

slug = project.lower()

root_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
src_dir = os.path.join(os.path.abspath(root_dir), 'src', slug)
ext_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'ext')
docs_modules_dir = os.path.join(os.path.abspath(root_dir), 'docs', 'modules')
tpl_dir = os.path.join(os.path.abspath(root_dir), 'docs', 'templates')

sys.path.insert(0, root_dir)
sys.path.insert(0, src_dir)
sys.path.insert(0, ext_dir)

#  from benchmarkstt.normalization import logger
# -- Auto build module docs --------------------------------------------------
sphinx_apidoc(['-e', '-f', '-t', tpl_dir, '-o', docs_modules_dir, src_dir])
os.remove(os.path.join(docs_modules_dir, 'modules.rst'))


# -- Auto build api docs -----------------------------------------------------

with open(os.path.join(os.path.abspath(root_dir), 'docs', 'api-methods.rst'), 'w') as f:
    f.write("Available JSON-RPC methods\n==========================\n\n\n")
    f.write(".. attention::\n\n")
    f.write("    Only supported for Python versions 3.6 and above\n\n\n")

    methods = get_methods()
    for name, func in methods.items.items():
        f.write('\n%s\n%s\n' % (name, '-' * len(name)))
        f.write('\n')
        f.write(format_docs(func.__doc__))
        f.write('\n\n')

# -- Auto build UML diagrams -------------------------------------------------
import uml
uml_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '_static', 'autogen')
uml.generate(src_dir, uml_dir)


# -- Set extensions ----------------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinxarg.ext',
    'sphinxcontrib.gravizo',
    'sphinxcontrib.mermaid',
]

# -- Setting readthedocs theme and config -----------------------------------

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme

    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
else:
    html_theme = 'default'

# -- Project information -----------------------------------------------------

with open('../VERSION') as f:
    # The full version, including alpha/beta/rc tags
    release = f.read()

# The short X.Y version
version = '.'.join(release.split('.', 3)[:2])


# -- General configuration ---------------------------------------------------

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = 'en'
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------

html_static_path = ['_static']

html_css_files = [
    'theme_overrides.css',
]

# -- Options for LaTeX output ------------------------------------------------

# mermaid -> svg, requires `yarn install` for this to be available (see Makefile)
mermaid_cmd = "./node_modules/.bin/mmdc"

latex_elements = {
    'papersize': 'a4paper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, '%s.tex' % (slug,), '%s Documentation' % (project,),
     author, 'manual'),
]

# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('cli', slug, '%s Documentation' % (project,),
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, project, '%s Documentation' % (project,),
     author, project, 'Description',
     'Miscellaneous'),
]


# -- Options for Epub output -------------------------------------------------

# Bibliographic Dublin Core info.
epub_title = project

# The unique identifier of the text. This can be a ISBN number
# or the project homepage.
#
# epub_identifier = ''

# A unique identification for the text.
#
# epub_uid = ''

# A list of files that should not be packed into the epub file.
epub_exclude_files = ['search.html']

#
# # -- Extension configuration -------------------------------------------------


smartquotes = False
# smartquotes_action = 'q'
#
# smartquotes_excludes = {'builders': ['man', 'text']}

highlight_language = 'none'
autodoc_default_values = {
    'members': None,
    'undoc-members': None,
    'special-members': None,
    'show-inheritance': None,
    'member-order': 'bysource',
    'exclude-members': '__dict__,__weakref__,__module__',
}


def setup(app):
    from autoclassmembersdiagram import MermaidClassMembersDiagram
    app.add_directive('autoclassmemberstree', MermaidClassMembersDiagram)

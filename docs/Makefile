# Minimal makefile for Sphinx documentation
#

PYTHON       := $(shell test -e ../env/bin/activate && echo "../env/bin/python" || echo "python3")

# You can set these variables from the command line.
SPHINXOPTS    =
SPHINXBUILD   = $(PYTHON) -msphinx
SOURCEDIR     = .
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

clean:
	for f in modules/*.rst; do [ -e "$$f" ] && rm modules/*.rst; break; done
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

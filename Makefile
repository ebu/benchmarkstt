.PHONY: docs test clean

test:
	pytest --verbose

docs: html

html:
	cd docs/ && make clean html && touch build/html/.nojekyll

man: build-man
	cp resources/manpage/*.1 /usr/local/share/man/man1

build-man:
	cd docs/ && make clean man
	cp docs/build/man/* resources/manpage/

clean:
	cd docs/ && make clean

gh-pages: # docs
	TMPFILE=$(shell mktemp); \
	cd docs/build/html/ && tar cf $$TMPFILE . ;\
	cd ../../..; \
	git checkout gh-pages; \
	tar xf $$TMPFILE; \
	rm $$TMPFILE; \
	echo "ready to commit"


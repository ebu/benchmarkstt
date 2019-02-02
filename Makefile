.PHONY: docs test clean

test:
	pytest --verbose

docs: html man

html:
	cd docs/ && make html

man: build-man
	cp resources/manpage/*.1 /usr/local/share/man/man1

build-man:
	cd docs/ && make man
	cp docs/build/man/* resources/manpage/

clean:
	cd docs/ && make clean

gh-pages:
	cd docs && make clean && make html && make doctest
	# todo: copy docs/build/html into gh-pages branch


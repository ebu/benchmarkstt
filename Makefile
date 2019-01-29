.PHONY: docs test clean

test:
	cd docs/ && make doctest

docs:
	cd docs/ && make html

clean:
	cd docs/ && make clean

gh-pages:
	cd docs && make clean && make html && make doctest
	# todo: copy docs/build/html into gh-pages branch


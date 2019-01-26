.PHONY: docs test clean

test:
	cd docs/; make doctest

docs:
	cd docs/; make html

clean:
	cd docs/; make clean

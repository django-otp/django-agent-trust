.PHONY: full
full: clean sdist wheel

.PHONY: sdist
sdist:
	python setup.py sdist

.PHONY: wheel
wheel:
	python setup.py bdist_wheel

.PHONY: upload
upload:
	twine upload dist/*

.PHONY: clean
clean:
	-rm -r build
	-rm -r dist
	-rm -r src/*.egg-info

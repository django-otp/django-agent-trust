.PHONY: all
all: clean sdist wheel

.PHONY: sdist
sdist:
	python setup.py sdist

.PHONY: wheel
wheel:
	python setup.py bdist_wheel

.PHONY: sign
sign: sdist wheel
	for f in dist/*.gz dist/*.whl; do \
	    gpg --detach-sign --armor $$f; \
	done

.PHONY: upload
upload: sign
	twine upload dist/*

.PHONY: clean
clean:
	-rm -r build
	-rm -r dist
	-rm -r *.egg-info

default: all

all:
	python setup.py build

install: all
	python setup.py install

clean:
	rm -f *.pyc
	cd tests && rm -f *.pyc
	cd cronwrapper && rm -f *.pyc
	rm -f MANIFEST
	rm -Rf build
	rm -Rf dist
	rm -Rf cronwrapper.egg-info
	rm -Rf cronwrapper/__pycache__
	rm -Rf tests/__pycache__
	rm -f tests/conf.py
	rm -f tests/auth.txt

sdist: clean
	python setup.py sdist

test:
	flake8 .
	cd tests && nosetests --exe

upload:
	python setup.py sdist register upload

release: test clean upload clean

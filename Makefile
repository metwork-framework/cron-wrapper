default: all

all:
	python setup.py build

install: all
	python setup.py install

clean:
	rm -f *.pyc
	rm -f tests/*.pyc
	rm -f MANIFEST
	rm -Rf build
	rm -Rf dist
	rm -Rf cronwrapper.egg-info
	rm -Rf cronwrapper/*.pyc
	rm -Rf cronwrapper/__pycache__
	rm -Rf tests/__pycache__
	rm -f tests/conf.py
	rm -f tests/auth.txt

sdist: clean
	python setup.py sdist

test_nose:
	flake8 cronwrapper tests
	cd tests && nosetests --exe

test_nose2:
	flake8 cronwrapper tests
	cd tests && nose2

upload:
	python setup.py sdist register upload

release: test clean upload clean

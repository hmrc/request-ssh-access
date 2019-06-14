.EXPORT_ALL_VARIABLES:

version = $(shell python setup.py --version)

init:
	pip install -i https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips/simple pipenv --upgrade
	pipenv install --dev

clean:
	rm -rf build dist request_ssh_access.egg-info

flake: clean
	pipenv run flake8 --exclude __init__.py --ignore E501

build: flake
	pipenv run python setup.py sdist bdist_wheel

publish: build
	pipenv run twine upload --repository-url https://artefacts.tax.service.gov.uk/artifactory/api/pypi/pips dist/*
	git tag -a v$$version -m v$$version
	git push --tags


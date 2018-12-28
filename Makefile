# Run make help or make list to find out what the commands are

VERSION_FILE=VERSION
VERSION:=$(shell cat $(VERSION_FILE) )


# ensures list is not mis-identified with a file of the same name
.PHONY: bumpmajor bumpminor bumppatch bumpbuild bumprelease
.PHONY: docker_local docker_pushdev docker_pushprod
.PHONY: clean_pyc list help


bumpmajor:
	@echo Deploying major update
	bumpversion major
	@${deploy_commands}
	git push
	git push --tags

bumpminor:
	@echo Deploying minor update
	bumpversion minor
	@${deploy_commands}
	git push
	git push --tags

bumppatch:
	@echo Deploying patch update
	bumpversion --allow-dirty patch
	${deploy_commands}
	git push
	git push --tags

bumpbuild:
	@echo Bumping build number
	bumpversion build
	git push
	git push --tags

bumprelease:
	@echo Bumping release and tagging
	bumpversion --tag release
	git push
	git push --tags



docker_local:
	@echo Building local docker image
	docker build -t biosearch/biosearch:localdev ./docker


docker_pushdev: bumpbuild
	@echo Deploying docker Staging image to dockerhub $(VERSION)
	git checkout develop

	docker build -t biosearch/biosearch:dev -t biosearch/biosearch:$(VERSION) ./docker
	docker push biosearch/biosearch:dev
	docker push biosearch/biosearch:$(VERSION)


docker_pushprod:
	@echo Deploying docker PROD image to dockerhub $(VERSION)
	git checkout master

	docker build -t biosearch/biosearch:latest -t biosearch/biosearch:$(VERSION) ./docker
	docker push biosearch/biosearch:latest
	docker push biosearch/biosearch:$(VERSION)


clean_pyc:
	find . -name '*.pyc' -exec rm -r -- {} +
	find . -name '*.pyo' -exec rm -r -- {} +
	find . -name '__pycache__' -exec rm -r -- {} +


# Local virtualenv test runner with biosearch test environment
# add --pdb to get dropped into a debugging env
tests: clean_pyc
	py.test -x -rs --cov=./biosearch --cov-report html --cov-config .coveragerc -c tests/pytest.ini --color=yes --durations=10 --flakes --pep8 tests


list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

help:
	@echo "List of commands"
	@echo "   help -- This listing "
	@echo "   list -- Automated listing of all targets"


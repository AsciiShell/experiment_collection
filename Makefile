PROJECT_NAME ?= experiment_collection
VERSION = $(shell python3 setup_server.py --version | tr '+' '-')
PROJECT_NAMESPACE ?= asciishell
REGISTRY_IMAGE ?= $(PROJECT_NAMESPACE)/$(PROJECT_NAME)

all:
	@echo "make clean				- Remove files created by distutils"
	@exit 0

clean:
	rm -rf *.egg-info build

codegen:
	python -m grpc_tools.protoc -I=src/ --python_out=src/ --grpc_python_out=src/ src/experiment_collection_core/*.proto

sdist_client: clean
	python3 setup_client.py sdist bdist_wheel

sdist_server: clean
	python3 setup_server.py bdist_wheel

docker: sdist_server
	docker build -t $(PROJECT_NAME):$(VERSION) .

pylint:
	pylint --rcfile=setup.cfg  -j 0 src/

flake8:
	flake8 --config=setup.cfg src/

bandit:
	 bandit --ini setup.cfg -r src/

linters: pylint flake8 bandit
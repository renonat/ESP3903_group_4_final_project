venv:
	python3 -m venv venv

.PHONY: development
development: venv
	pip install -r requirements.txt

.PHONY: server
server: development
	python3 -m lecture_system.server

.PHONY: test
test: development
	mypy .

.PHONY: clean
clean:
	rm -rf venv

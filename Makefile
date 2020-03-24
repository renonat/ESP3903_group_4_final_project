venv:
	python3 -m venv venv

.PHONY: development
development: venv
	pip install -r requirements.txt

.PHONY: server
server: development
	export FLASK_ENV=development
	export FLASK_APP=server.py
	flask run

.PHONY: test
test: development
	mypy .

.PHONY: clean
clean:
	rm -rf venv

venv:
	python3 -m venv venv

development: venv
	pip install -r requirements.txt

clean:
	rm -rf venv

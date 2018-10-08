
test:
	python tests.py
	pylint log_parse.py
	pycodestyle log_parse.py


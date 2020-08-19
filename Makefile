clean:
	rm -rf dist *.egg-info .pytest_cache htmlcov .coverage coverage.xml .DS_Store
	find . -name "*.pyc" -exec rm -f {} \;

check:
	poetry run isort . --check
	poetry run black --check .
	poetry run flake8 .

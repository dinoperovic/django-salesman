check:
	poetry run isort --check-only
	poetry run black --check .
	poetry run flake8 .

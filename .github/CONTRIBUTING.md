# Contributing

Thank you for your interest in contributing to Salesman.

Before you continue please consider discussing your desired changes using an issue tracker.

## Setup

To get started you should fork and clone the repo, then setup your project using [Poetry](https://python-poetry.org/):

```bash
poetry install --extras "tests docs"
poetry run pre-commit install
```

You can manually run tests and lint using:
```bash
poetry run pytest
poetry run pre-commit run --all-files
```

## Pull request

When you're ready, open up a pull request and we'll go from there.

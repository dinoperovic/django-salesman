# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import datetime
import os
import sys

import django  # noqa

import salesman  # noqa

sys.path.insert(0, os.path.abspath("../"))
sys.path.insert(0, os.path.abspath("../example"))


os.environ["DJANGO_SETTINGS_MODULE"] = "example.project.settings"
django.setup()

# -- Project information -----------------------------------------------------

project = salesman.__title__
author = salesman.__author__
copyright = f"{datetime.date.today().year}, {author}"
version = salesman.__version__
release = salesman.__version__

# -- General configuration ---------------------------------------------------

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx_rtd_theme",
    "sphinxcontrib.httpdomain",
]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# autodoc
autodoc_member_order = "bysource"


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_theme_options = {
    "logo_only": True,
}
html_logo = "_static/logo.svg"

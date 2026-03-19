import os
import sys

sys.path.insert(0, os.path.abspath("../.."))

project = "LostAndFound"
copyright = "2026, N/A"
author = "N/A"
release = "1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

autodoc_mock_imports = ["tkinter"]
autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": False,
}

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "alabaster"
html_static_path = ["_static"]

latex_engine = "pdflatex"

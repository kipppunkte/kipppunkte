python3.9  -m venv .venv
python -m pip install mkdocs-material
python -m mkdocs build
python -m mkdocs gh-deploy

# mkdocs new .
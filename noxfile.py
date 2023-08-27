from pathlib import Path

import nox

root = Path(__file__).parent.resolve()
venvDir = root / ".venv"

nox.options.sessions = ['serve']
nox.options.error_on_external_run = True
nox.options.error_on_missing_interpreters = True


@nox.session(python=False, venv_backend='none', reuse_venv=True)
def lint(session):
    venvDir.joinpath("bin/python")
    pip = venvDir.joinpath("bin/pip")
    session.run(str(pip), "install", "-r", "requirements.txt")

@nox.session(python=False, venv_backend='none', reuse_venv=True)
def serve(session):
    mkdocs = venvDir.joinpath("bin/mkdocs")
    session.run(str(mkdocs), "serve")

@nox.session(python=False, venv_backend='none', reuse_venv=True)
def deploy(session):
    mkdocs = venvDir.joinpath("bin/mkdocs")
    session.run(str(mkdocs), "gh-deploy")
from pathlib import Path

import nox

root = Path(__file__).parent.resolve()
venvDir = root / ".venv"

nox.options.sessions = ['serve']
nox.options.error_on_external_run = True
nox.options.error_on_missing_interpreters = True

def refresh_deps(session):
    pip = venvDir.joinpath("bin/pip")
    session.run(str(pip), "install", "-r", "requirements.txt")
    session.run("find", ".", "-iname", "*.Identifier" "-delete")



@nox.session(python=False, venv_backend='none', reuse_venv=True)
def serve(session):
    refresh_deps(session)
    mkdocs = venvDir.joinpath("bin/mkdocs")
    session.run(str(mkdocs), "serve")

@nox.session(python=False, venv_backend='none', reuse_venv=True)
def deploy(session):
    refresh_deps(session)
    mkdocs = venvDir.joinpath("bin/mkdocs")
    session.run(str(mkdocs), "gh-deploy")


@nox.session(python=False, venv_backend='none', reuse_venv=True)
def urls(session):
    '''
    URL;QR Code Title (for reference)
    http://www.your-website.com;My QR Code 1
    http://www.your-website.com;My QR Code 2
    http://www.your-website.com;My QR Code 3
    '''
    site = 'https://kipppunkte.github.io/kipppunkte'
    lines = ["URL;QR Code Title (for reference)"]
    lines += [f"{site};Homepage"]
    for sid in range(1, 51):
        lines.append(site + f'/Station_{sid:02d};Section_{sid:02d}')
    lines.append("")
    Path("./qr_codes.csv").write_text("\n".join(lines))
    session.run("cat", "qr_codes.csv")



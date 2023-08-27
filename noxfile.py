from pathlib import Path
import logging

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
def build(session):
    refresh_deps(session)
    mkdocs = venvDir.joinpath("bin/mkdocs")
    session.run(str(mkdocs), "build")



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



DOCS_PATH = Path("./docs")
ASSETS_PATH = DOCS_PATH / "assets"
DATA_PATH = Path("GoogleDocs")
PNG_FILES = sorted(DATA_PATH.glob("*.png"))


TPL = r'''
# Station #s_id#: #s_name#


===+ "Auftrag"

    ![Image title](assets/#image_url_a#){: style="max-height:60vh" }


=== "Ergebniss"

    ![Image title](assets/#image_url_b#){: style="max-height:60vh" }
'''

@nox.session(python=False, venv_backend='none', reuse_venv=True)
def urls(session):
    site = 'https://kipppunkte.github.io/kipppunkte'
    stations = Path("stations.txt").read_text().split("\n")
    stations = [_.split("\t", 1) for _ in stations if _.strip()]
    res = []
    toc = []
    toc1 = []

    for s_id, s_name in stations:
        fname = DOCS_PATH / f"{s_id}.md"
        png_fnames = sorted(
            DATA_PATH.glob(f"{s_id}_*.png")
        )
        png0 = None
        png1 = None
        import shutil
        text = TPL.replace("#s_id#", s_id).replace("#s_name#", s_name)
        logging.info((s_id, s_name))
        # logging.info(png_fnames)
        if len(png_fnames) == 2:
            png0 = ASSETS_PATH / png_fnames[0].name
            shutil.copy2(png_fnames[0], png0)
            png1 = ASSETS_PATH / png_fnames[1].name
            shutil.copy2(png_fnames[1], png1)            
            text = text.replace("#image_url_a#", png0.name).replace("#image_url_b#", png1.name)
            # logging.info("Found 2 files.")
        elif len(png_fnames) == 1:
            png0 = ASSETS_PATH / png_fnames[0].name
            shutil.copy2(png_fnames[0], png0)          
            text = text.replace("#image_url_a#", png0.name).replace("#image_url_b#", png0.name)
            logging.warn("Found just 1 file.")
        else:
            logging.error("Found no file.")
        fname.write_text(text)
        toc.append(
            f'- "Station {s_id}: {s_name}": {fname.name}'
        )
        toc1.append(
            f'- [Station {s_id}: {s_name}]({fname.name}) (n={len(png_fnames)})'
        )
    Path("staging/test.yaml").write_text('\n'.join(toc))
    Path("staging/test1.md").write_text('\n'.join(toc1))
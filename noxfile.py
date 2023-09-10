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
    
    refresh_deps(session)
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
SITE = 'https://kipppunkte.github.io/kipppunkte'


TPL_PICS = r'''
# Station #s_id#: #s_name#


===+ "Auftrag"

    ![Image title](assets/#image_url_a#){: style="max-height:60vh" }


=== "Ergebniss"

    ![Image title](assets/#image_url_b#){: style="max-height:60vh" }
'''

TPL_AUDIO = r'''
# Station #s_id#: #s_name#

Audio: 

<audio controls>
  <source src="https://github.com/kipppunkte/kipppunkte/raw/gh-pages/assets/ytmp3free.cc_keke-ladies-prod-fvlcrvm-youtubemp3free.org.mp3" type="audio/mpeg">
  Your browser does not support the audio tag.
</audio>
'''

def create_gmaps_link(lon, lat):
    return rf"https://www.google.com/maps/dir/?api=1&travelmode=walking&destination={lon},{lat}"


@nox.session(python=False, venv_backend='none', reuse_venv=True)
def gmaps(session):
    # pip install beautifulsoup4
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(Path("Kipppunkte.kml").read_text(), 'lxml')
    print(soup)
    stations = Path("stations.txt").read_text().split("\n")
    stations = [_.split("\t", 4) for _ in stations if _.strip()]
    for s_id, s_name, s_pics, s_audio in stations:
        pass


@nox.session(python=False, venv_backend='none', reuse_venv=True)
def urls(session):
    site = 'https://kipppunkte.github.io/kipppunkte'
    stations = Path("stations.txt").read_text().split("\n")
    stations = [_.split("\t", 4) for _ in stations if _.strip()]
    res = []
    toc = []
    toc1 = []
    urls = [
        f'{SITE};"Homepage"'
    ]
    txt_md = []
    txt_md.append(f"- [ ]  Homepage")
    txt_md.append(f"```")
    txt_md.append(f'{SITE}')
    txt_md.append(f"```")
    txt_md.append(f"```")
    txt_md.append(f'Homepage.svg')
    txt_md.append(f"```")

    for s_id, s_name, is_game, s_pics, s_audio in stations:
        s_pics = s_pics.lower() == "x"
        s_audio = s_audio.lower() == "x"

        s_both = s_pics != s_audio
        logging.info(s_both)
        # assert s_pics != s_audio

        fname = DOCS_PATH / f"{s_id}.md"

        import shutil
        
        logging.info((s_id, s_name, s_pics, s_audio))
        tag = "(pic)" if s_pics else "(audio)"
        n_expected = 2 if s_pics else 1
        if s_pics:
            f_names = sorted(
                DATA_PATH.glob(f"{s_id}_*.png")
            )
            png0 = None
            png1 = None
            text = TPL_PICS.replace("#s_id#", s_id).replace("#s_name#", s_name)
            if len(f_names) == 2:
                png0 = ASSETS_PATH / f_names[0].name
                shutil.copy2(f_names[0], png0)
                png1 = ASSETS_PATH / f_names[1].name
                shutil.copy2(f_names[1], png1)            
                text = text.replace("#image_url_a#", png0.name).replace("#image_url_b#", png1.name)
                # logging.info("Found 2 files.")
            elif len(f_names) == 1:
                png0 = ASSETS_PATH / f_names[0].name
                shutil.copy2(f_names[0], png0)          
                text = text.replace("#image_url_a#", png0.name).replace("#image_url_b#", png0.name)
                logging.warn("Found just 1 file.")
            else:
                logging.error("Found no file.")
        elif s_audio:
            text = TPL_AUDIO.replace("#s_id#", s_id).replace("#s_name#", s_name)
            f_names = sorted(
                DATA_PATH.glob(f"{s_id}_*.mp3")
            )

        fname.write_text(text)
        toc.append(
            f'- "Station {s_id}: {s_name}": {fname.name}'
        )
        toc1.append(
            f'- [Station {s_id}: {s_name}]({fname.name}) {tag}(n={len(f_names)}/{n_expected})'
        )
        urls.append(f'{site}/{fname.stem};"Station {s_id}: {s_name}"')
        txt_md.append(f"- [ ]  Station {s_id}: {s_name}")
        txt_md.append(f"```")
        txt_md.append(f'{site}/{fname.stem}')
        txt_md.append(f"```")
        txt_md.append(f"```")
        txt_md.append(f'{fname.stem}.svg')
        txt_md.append(f"```")

    Path("staging/test.yaml").write_text('\n'.join(toc))
    Path("staging/test1.md").write_text('\n'.join(toc1))
    Path("staging/urls.csv").write_text('\n'.join(urls))
    Path("staging/urls.md").write_text('\n'.join(txt_md))
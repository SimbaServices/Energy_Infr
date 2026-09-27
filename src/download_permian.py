"""Download public RRC files for Texas Permian lease locations.

Gas disposition (already retrieved separately):
  data/raw/rrc/gsf102 and olf102

This script retrieves, for each Permian county:
  data/raw/rrc/api/ccXXX   statewide API extract, folder 2026-09-23
  data/raw/rrc/wells/wellXXX.zip   surface-well shapefile
"""
import re
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar
from pathlib import Path

POST = "https://mft.rrc.texas.gov/webclient/godrive/PublicGoDrive.xhtml"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "rrc"
COUNTIES = [
    "003", "033", "103", "105", "109", "115", "135", "165", "169", "173",
    "227", "235", "301", "317", "329", "335", "371", "383", "389", "415",
    "431", "443", "461", "475", "495", "501",
]


def opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def call(op, url, data=None, referer=None, ajax=False, timeout=300):
    headers = {"User-Agent": "Mozilla/5.0"}
    if referer:
        headers["Referer"] = referer
    if data is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        if ajax:
            headers["Faces-Request"] = "partial/ajax"
            headers["X-Requested-With"] = "XMLHttpRequest"
    req = urllib.request.Request(url, data=data, headers=headers)
    with op.open(req, timeout=timeout) as response:
        return response.read()


def viewstate(text):
    match = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', text)
    if match:
        return match.group(1)
    match = re.search(
        r"<update id=\"j_id__v_0:javax.faces.ViewState[^>]*><!\[CDATA\[(.*?)\]\]>",
        text,
    )
    if match:
        return match.group(1).strip()
    raise RuntimeError("no viewstate")


def file_index(html):
    return dict(re.findall(r'id="fileTable:(\d+):j_id_2f"[^>]*>([^<]+)<', html))


def download_named(op, referer, view, row, dest: Path):
    if dest.exists() and dest.stat().st_size > 1000:
        print("keep", dest.name, dest.stat().st_size)
        return
    field = f"fileTable:{row}:j_id_2f"
    body = call(
        op,
        POST,
        urllib.parse.urlencode(
            {"javax.faces.ViewState": view, "fileList_SUBMIT": "1", field: field}
        ).encode(),
        referer,
    )
    if body[:1] == b"<" or body[:5] == b"<?xml":
        raise RuntimeError(f"{dest.name} returned HTML ({len(body)} bytes)")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
    print("got", dest.name, len(body))


def ajax(op, referer, form):
    return call(op, POST, urllib.parse.urlencode(form).encode(), referer, ajax=True).decode(
        "utf-8", "replace"
    )


def page_form(view, first):
    return {
        "javax.faces.partial.ajax": "true",
        "javax.faces.source": "fileTable",
        "javax.faces.partial.execute": "fileTable",
        "javax.faces.partial.render": "fileTable",
        "javax.faces.behavior.event": "page",
        "javax.faces.partial.event": "page",
        "fileTable_pagination": "true",
        "fileTable_first": str(first),
        "fileTable_rows": "250",
        "fileTable_skipChildren": "true",
        "fileTable_encodeFeature": "true",
        "fileList_SUBMIT": "1",
        "javax.faces.ViewState": view,
    }


def download_wells():
    link = "https://mft.rrc.texas.gov/link/d551fb20-442e-4b67-84fa-ac3f23ecabb4"
    op = opener()
    page = call(op, link).decode("utf-8", "replace")
    view = viewstate(page)
    names = {name: row for row, name in file_index(page).items()}
    for code in COUNTIES:
        name = f"well{code}.zip"
        if name not in names:
            continue
        download_named(op, link, view, names[name], OUT / "wells" / name)
    if "well501.zip" not in names:
        paged = ajax(op, link, page_form(view, 250))
        view = viewstate(paged)
        extra = {name: row for row, name in file_index(paged).items()}
        if "well501.zip" not in extra:
            print("missing well501.zip")
        else:
            download_named(op, link, view, extra["well501.zip"], OUT / "wells" / "well501.zip")


def download_api():
    link = "https://mft.rrc.texas.gov/link/701db9a3-32b5-488d-812b-cd6ff7d0fe85"
    op = opener()
    page = call(op, link).decode("utf-8", "replace")
    view = viewstate(page)
    paged = ajax(op, link, page_form(view, 250))
    view = viewstate(paged)
    match = re.search(r'id="(fileTable:\d+:j_id_2d)"[^>]*>2026-09-23<', paged)
    if not match:
        raise RuntimeError("2026-09-23 API folder not on the second page")
    source = match.group(1)
    inside = ajax(
        op,
        link,
        {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": source,
            "javax.faces.partial.execute": source,
            "javax.faces.partial.render": "breadcrumbForm fileList toolbarForm messages",
            "fileList_SUBMIT": "1",
            "javax.faces.ViewState": view,
            source: source,
        },
    )
    view = viewstate(inside)
    names = {name: row for row, name in file_index(inside).items()}
    for code in COUNTIES:
        name = f"maf016.cc{code}"
        if name not in names:
            continue
        download_named(op, link, view, names[name], OUT / "api" / f"cc{code}")
    if "maf016.cc501" not in names:
        paged = ajax(op, link, page_form(view, 250))
        view = viewstate(paged)
        extra = {name: row for row, name in file_index(paged).items()}
        if "maf016.cc501" not in extra:
            print("missing maf016.cc501")
        else:
            download_named(op, link, view, extra["maf016.cc501"], OUT / "api" / "cc501")


if __name__ == "__main__":
    download_wells()
    download_api()

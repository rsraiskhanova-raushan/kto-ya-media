# Генератор карусельных слайдов и обложек постов (1080x1350) для Instagram.
# Запуск: python3 tools/slides.py <fonts_dir>  → картинки в carousels/ и posts/
import json, sys, html, os, asyncio, base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "tools" / "fonts"
DATA = json.loads((ROOT / "tools" / "slides.json").read_text(encoding="utf-8"))

def faces():
    css = []
    spec = [("Cormorant Garamond", "fontsource-cormorant-garamond-5.0.13", "cormorant-garamond", (500, 600, 700)),
            ("Inter", "fontsource-inter-5.0.18", "inter", (400, 500, 600, 700))]
    for fam, pkg, base, ws in spec:
        for w in ws:
            for sub, rng in (("cyrillic", "U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116"),
                             ("latin", "U+0000-00FF,U+2000-206F,U+20B8,U+2190-21FF,U+2713")):
                p = FONTS / pkg / "files" / f"{base}-{sub}-{w}-normal.woff2"
                css.append(f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{base64.b64encode(p.read_bytes()).decode()}) format('woff2');unicode-range:{rng}}}")
    return "\n".join(css)

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px}
body{font-family:Inter,sans-serif;color:#2A1F27;background:#F7F2EE;-webkit-font-smoothing:antialiased}
.s{position:relative;width:1080px;height:1350px;padding:96px 96px 0;display:flex;flex-direction:column;overflow:hidden}
.dark{background:#5A2550;color:#FBF6F9}
.top{display:flex;justify-content:space-between;align-items:center;font-size:24px;letter-spacing:.12em;text-transform:uppercase;color:#8A6F80}
.dark .top{color:#D9B8CC}
.pg{font-variant-numeric:tabular-nums;letter-spacing:.04em}
.kick{margin-top:0;font-size:30px;font-weight:600;color:#6B2D5C;letter-spacing:.02em}
.dark .kick{color:#F0C9E0}
h1{font-family:'Cormorant Garamond',serif;font-weight:700;line-height:1.04;letter-spacing:-.01em}
.k-cover h1{font-size:108px;font-weight:700;margin-top:12px}
.k-content h1{font-size:84px;margin-top:20px}
.body{margin-top:44px;font-size:42px;line-height:1.45;color:#3B2E37}
.dark .body{color:#F3E6EE}
.body p+p{margin-top:24px}
.acc{margin-top:56px;border-left:6px solid #6B2D5C;padding:26px 30px 26px 34px;font-size:40px;line-height:1.4;font-weight:500;background:rgba(107,45,92,.06)}
.dark .acc{border-color:#F0C9E0;background:rgba(255,255,255,.08)}
.acc b{color:#6B2D5C;font-weight:700}
.dark .acc b{color:#F0C9E0}
.sub{margin-top:48px;font-size:40px;line-height:1.4;color:#5B4855}
.dark .sub{color:#EAD7E3}
.foot{position:absolute;left:96px;right:96px;bottom:64px;display:flex;justify-content:space-between;align-items:center;font-size:24px;color:#8A6F80}
.dark .foot{color:#D9B8CC}
.swipe{font-size:28px;font-weight:600;color:#6B2D5C}
.dark .swipe{color:#F0C9E0}
.cta{margin-top:64px;display:inline-block;align-self:flex-start;background:#FBF6F9;color:#5A2550;border-radius:22px;padding:30px 46px;font-size:40px;font-weight:700}
.light .cta{background:#6B2D5C;color:#fff}
.k-cta h1{font-size:96px;font-weight:700}
.mid{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:140px}
.k-content .mid h1{margin-top:20px}
.has-num h1{padding-right:170px}
.rule{width:120px;height:6px;background:#6B2D5C;margin-top:56px}
.dark .k-cta h1{font-size:96px;font-weight:700}
.rule{background:#F0C9E0}
.big{font-family:'Cormorant Garamond',serif;font-size:420px;line-height:.8;color:rgba(107,45,92,.09);position:absolute;right:60px;bottom:120px;font-weight:700}
.dark .big{color:rgba(255,255,255,.08)}
"""

def rich(t):
    # **текст** → <b>
    parts = html.escape(t).split("**")
    return "".join(f"<b>{p}</b>" if i % 2 else p for i, p in enumerate(parts))

def slide_html(sl, i, n, theme):
    kind = sl.get("type", "content")
    dark = sl.get("dark", kind in ("cover", "cta") and theme == "dark")
    cls = "dark" if dark else "light"
    top = f'<div class="top"><span>Кто я · Academia369</span><span class="pg">{i}/{n}</span></div>' if n > 1 else '<div class="top"><span>Кто я · Academia369</span><span></span></div>'
    big = f'<div class="big">{html.escape(sl["num"])}</div>' if sl.get("num") else ""
    inner = ""
    if sl.get("kick"): inner += f'<div class="kick">{rich(sl["kick"])}</div>'
    inner += f'<h1>{rich(sl["title"])}</h1>'
    if kind in ("cover",): inner += '<div class="rule"></div>'
    if sl.get("sub"): inner += f'<div class="sub">{rich(sl["sub"])}</div>'
    if sl.get("body"): inner += '<div class="body">' + "".join(f"<p>{rich(p)}</p>" for p in sl["body"]) + "</div>"
    if sl.get("acc"): inner += f'<div class="acc">{rich(sl["acc"])}</div>'
    if sl.get("cta"): inner += f'<div class="cta">{rich(sl["cta"])}</div>'
    right = '<span class="swipe">Листайте →</span>' if (kind == "cover" and n > 1) else "<span>@raushan_raiskhanova</span>"
    foot = f'<div class="foot"><span>Раушан Райсханова</span>{right}</div>'
    numcls = ' has-num' if sl.get('num') else ''
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{FACES}{BASE_CSS}</style></head><body><div class="s k-{kind} {cls}{numcls}">{big}{top}<div class="mid">{inner}</div>{foot}</div></body></html>'

FACES = faces()

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for set_ in DATA:
            out = ROOT / set_["dir"]
            out.mkdir(parents=True, exist_ok=True)
            n = len(set_["slides"])
            for i, sl in enumerate(set_["slides"], 1):
                await pg.set_content(slide_html(sl, i, n, set_.get("theme", "dark")))
                await pg.wait_for_timeout(150)
                await pg.screenshot(path=str(out / f"{i:02d}.jpg"), type="jpeg", quality=92)
            print(set_["dir"], n)
        await b.close()

asyncio.run(main())

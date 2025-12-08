
import os, json, re, pathlib, html, textwrap, datetime
from dotenv import load_dotenv
load_dotenv()
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "products.json"
DIST = ROOT / "dist" / "shop"
ASSETS = ROOT / "assets"
TPL = ROOT / "templates"
DIST.mkdir(parents=True, exist_ok=True)
YEAR = str(datetime.datetime.utcnow().year)
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://www.fallat.digital").rstrip("/")
GA4_ID = os.getenv("GA4_MEASUREMENT_ID","").strip()
GA4 = '<script async src="https://www.googletagmanager.com/gtag/js?id={{MEASUREMENT_ID}}"></script>\n<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag(\'js\',new Date());gtag(\'config\',\'{{MEASUREMENT_ID}}\');</script>'.replace("{MEASUREMENT_ID}", GA4_ID) if GA4_ID else ""

def slugify(s:str)->str:
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s or "product"

products = json.loads(DATA.read_text(encoding="utf-8"))
for p in products:
    if not p.get("id"): p["id"]=slugify(p.get("name","product"))
    if not p.get("slug"): p["slug"]=slugify(p.get("name","product"))
    p.setdefault("category","Digital Product")
    p.setdefault("image_url","https://placehold.co/1200x800/png")
    p.setdefault("summary","")
    p.setdefault("details", p["summary"])
    p.setdefault("price_usd", 0)
    p.setdefault("payment_link_url","#")

tpl_product = (TPL/"product.html").read_text(encoding="utf-8")
for p in products:
    html_out = tpl_product
    html_out = html_out.replace("{SITE_BASE_URL}", SITE_BASE_URL)
    html_out = html_out.replace("{TITLE}", html.escape(p["name"]))
    html_out = html_out.replace("{SUMMARY}", html.escape(p["summary"]))
    html_out = html_out.replace("{CATEGORY}", html.escape(p.get("category","Digital Product")))
    html_out = html_out.replace("{IMAGE_URL}", html.escape(p["image_url"]))
    html_out = html_out.replace("{PRICE}", f"{p['price_usd']:.2f}".format(p=p))
    html_out = html_out.replace("{PAYMENT_LINK_URL}", html.escape(p["payment_link_url"]))
    html_out = html_out.replace("{DETAILS}", html.escape(p.get("details",p["summary"])).replace("\n","<br>"))
    html_out = html_out.replace("{SLUG}", p["slug"])
    html_out = html_out.replace("{YEAR}", YEAR)
    html_out = html_out.replace("{GA4}", GA4)
    (DIST/f"{p['slug']}.html").write_text(html_out, encoding="utf-8")

cards = []
for p in products:
    cards.append(f'''
    <a class="card" href="/shop/{p['slug']}.html">
      <img src="{p['image_url']}" alt="{p['name']}">
      <div class="pad">
        <div class="badge">{p.get('category','Digital Product')}</div>
        <div class="title">{p['name']}</div>
        <div class="price">${p['price_usd']:.2f}</div>
      </div>
    </a>''')
cards_html = "\n".join(cards) if cards else "<p class='muted'>No products yet.</p>"

tpl_index = (TPL/"index.html").read_text(encoding="utf-8")
index_html = tpl_index.replace("{PRODUCT_CARDS}", cards_html)
index_html = index_html.replace("{SITE_BASE_URL}", SITE_BASE_URL)
index_html = index_html.replace("{YEAR}", YEAR)
index_html = index_html.replace("{GA4}", GA4)
(DIST/"index.html").write_text(index_html, encoding="utf-8")

DIST_ASSETS = ROOT/"dist"/"assets"
DIST_ASSETS.mkdir(parents=True, exist_ok=True)
(DIST_ASSETS/"shop.css").write_text((ASSETS/"shop.css").read_text(encoding="utf-8"), encoding="utf-8")
print("Wrote", (DIST/"index.html").resolve())

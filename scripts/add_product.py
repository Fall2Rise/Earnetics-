
import json, pathlib, argparse, re, datetime
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "products.json"
def slugify(s:str)->str:
    s = s.lower().strip()
    s = re.sub(r'[^a-z0-9]+','-',s).strip('-')
    return s or "product"
ap = argparse.ArgumentParser(description="Add a product to data/products.json")
ap.add_argument("--name", required=True)
ap.add_argument("--price", type=float, required=True, help="USD price")
ap.add_argument("--link", required=True, help="Stripe Payment Link URL")
ap.add_argument("--summary", default="")
ap.add_argument("--details", default="")
ap.add_argument("--image-url", dest="image_url", default="https://placehold.co/1200x800/png")
ap.add_argument("--category", default="Digital Product")
args = ap.parse_args()
products = []
if DATA.exists():
    products = json.loads(DATA.read_text(encoding="utf-8"))
slug = slugify(args.name)
prod = {
    "id": slug, "slug": slug, "name": args.name,
    "price_usd": round(args.price, 2), "payment_link_url": args.link,
    "summary": args.summary, "details": args.details or args.summary,
    "image_url": args.image_url, "category": args.category,
    "created_at": datetime.datetime.utcnow().isoformat()+"Z", "published": True
}
products = [p for p in products if p.get("id") != slug]
products.append(prod)
DATA.write_text(json.dumps(products, indent=2), encoding="utf-8")
print("Added product:", slug); print("Now run:  python scripts/render_shop.py")

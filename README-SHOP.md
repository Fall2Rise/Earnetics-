
# Fallat Digital — Shop Starter Pack
This lets Fallat_CrewAI publish products to **www.fallat.digital** as static pages with Stripe buy buttons.
- Products live in `data/products.json`.
- Build pages with: `python scripts/render_shop.py` → output in `dist/shop/`.

## Quick use
1) `copy .env.example .env` → set `SITE_BASE_URL=https://www.fallat.digital`
2) Add a product:
   ```powershell
   python scripts/add_product.py --name "The 609 Machine" --price 47 ^
     --link "https://buy.stripe.com/your_link" ^
     --summary "Automated 609 toolkit." ^
     --image-url "https://your-cdn.com/609.jpg"
   ```
3) Build:
   ```powershell
   python scripts/render_shop.py
   start .\dist\shop\index.html
   ```
4) Deploy the `dist` folder to your host so it appears at `/shop`.

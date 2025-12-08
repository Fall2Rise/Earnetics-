import requests
from bs4 import BeautifulSoup
import json

url = "https://trends.google.com/trends/trendingsearches/daily"
params = {"geo": "US", "hl": "en-US"}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}
resp = requests.get(url, params=params, headers=headers)
soup = BeautifulSoup(resp.text, "html.parser")
next_data = soup.find("script", id="__NEXT_DATA__")
if not next_data:
    print("No NEXT data")
else:
    data = json.loads(next_data.string)
    print(data.keys())
    print(data.get("props", {}).keys())
    page_props = data.get("props", {}).get("pageProps", {})
    print(page_props.keys())

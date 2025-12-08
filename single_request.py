import requests

url = "https://trends.google.com/trends/trendingsearches/daily"
params = {
    "geo": "US",
    "hl": "en-US",
}
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}
resp = requests.get(url, params=params, headers=headers)
print(resp.status_code)
print(resp.text[:200])

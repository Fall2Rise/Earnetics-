import requests
import datetime
from collections import Counter
import json
import time

BASE_URL = "https://trends.google.com/trends/api/dailytrends"
PARAMS = {
    "hl": "en-US",
    "tz": "360",
    "geo": "US",
    "ns": "15",
}

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"}

start_date = datetime.date.today() - datetime.timedelta(days=1)
collector = Counter()
weekly_details = {}

for offset in range(0, 180, 7):
    ed = start_date - datetime.timedelta(days=offset)
    params = PARAMS | {"ed": ed.strftime("%Y%m%d")}
    resp = requests.get(BASE_URL, params=params, headers=headers)
    if resp.status_code != 200:
        print(f"Request failed for {params['ed']} with status {resp.status_code}")
        time.sleep(5)
        continue
    text = resp.text
    if text.startswith(")]}'"):
        text = text[5:]
    data = json.loads(text)
    trending = data.get("default", {}).get("trendingSearchesDays", [])
    day_terms = []
    for day in trending:
        for search in day.get("trendingSearches", []):
            query = search.get("title", {}).get("query")
            if query:
                collector.update([query.lower()])
                day_terms.append(query)
    weekly_details[ed.strftime("%Y-%m-%d")] = day_terms
    time.sleep(1)

report = {
    "top_terms": collector.most_common(50),
    "sampled_days": weekly_details
}

print(json.dumps(report, indent=2))

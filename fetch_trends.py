import requests
from bs4 import BeautifulSoup
import json

BASE_URL = 'https://explodingtopics.com/topics'
HEADERS = {'User-Agent': 'Mozilla/5.0'}
PERIOD = 6

resp = requests.get(BASE_URL, params={'period': PERIOD, 'page': 1}, headers=HEADERS)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, 'html.parser')
script = soup.find('script', string=lambda s: s and '__NEXT_DATA__' in s)
text = script.string
marker = ';__NEXT_LOADED_PAGES__'
text = text[:text.find(marker)]
data = json.loads(text[text.find('{'):])
trends = data['props']['pageProps']['data']['trends']

records = []
for trend in trends:
    growth = trend.get('growth', {})
    keyword = trend.get('keyword')
    records.append({
        'keyword': keyword,
        'topic': trend.get('topic'),
        'growth_3m': growth.get('3'),
        'growth_6m': growth.get('6'),
        'growth_12m': growth.get('12'),
        'search_volume': trend.get('keywordDataGlobal', {}).get('vol'),
        'description': trend.get('briefDescription'),
    })

records.sort(key=lambda x: (x['growth_6m'] or 0), reverse=True)
ai_related = [r for r in records if 'ai' in (r['keyword'] or '').lower() or 'automation' in (r['keyword'] or '').lower() or 'agent' in (r['keyword'] or '').lower()]

report = {
    'source': 'explodingtopics.com/topics?period=6',
    'period_months': PERIOD,
    'total_records': len(records),
    'top_records': records[:20],
    'ai_related': ai_related
}

print(json.dumps(report, indent=2))

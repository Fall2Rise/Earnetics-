import requests
from bs4 import BeautifulSoup
import json

url = 'https://explodingtopics.com/topics'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')
script = soup.find('script', string=lambda s: s and '__NEXT_DATA__' in s)
if not script:
    raise SystemExit('next data not found')
text = script.string
marker = ';__NEXT_LOADED_PAGES__'
idx = text.find(marker)
if idx != -1:
    text = text[:idx]
start = text.find('{')
json_str = text[start:]
data = json.loads(json_str)
page_props = data['props']['pageProps']
topics = page_props.get('topics', [])
print(len(topics))
for topic in topics[:20]:
    print(topic['topic'], topic.get('growth', ''), topic.get('searchVolume', ''))

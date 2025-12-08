import requests
from bs4 import BeautifulSoup
import json

url = 'https://explodingtopics.com/topics'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')
script = soup.find('script', string=lambda s: s and '__NEXT_DATA__' in s)
text = script.string
marker = ';__NEXT_LOADED_PAGES__'
idx = text.find(marker)
text = text[:idx]
start = text.find('{')
json_str = text[start:]
data = json.loads(json_str)
page_props = data['props']['pageProps']
print(page_props.keys())
print(page_props.get('topics') is None)
print(page_props.get('topicStableData') is None)
print(type(page_props.get('topicTableData')))

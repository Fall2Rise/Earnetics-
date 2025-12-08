import requests

url = 'https://trends.google.com/trends/trendingsearches/daily'
params = {'geo': 'US', 'hl': 'en-US'}
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, params=params, headers=headers)
print(resp.status_code)
print(resp.text[:1200])

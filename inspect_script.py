import requests
from bs4 import BeautifulSoup

url = 'https://explodingtopics.com/topics'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')
script = soup.find('script', string=lambda s: s and '__NEXT_DATA__' in s)
text = script.string
print(text[:200])
print('...')
print(text[-200:])

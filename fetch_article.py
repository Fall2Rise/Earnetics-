import requests
from bs4 import BeautifulSoup

url = "https://explodingtopics.com/topics"
headers = {"User-Agent": "Mozilla/5.0"}
resp = requests.get(url, headers=headers)
print(resp.status_code)
soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select('div.Topic_title__jaj3c')
for item in items[:20]:
    print(item.get_text(strip=True))

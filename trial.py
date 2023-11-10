from bs4 import BeautifulSoup
import requests

url = 'https://www.sofascore.com/standings/table-tennis/international/tt-elite-series/99281'

response = requests.get(url)
print(response.request.url)
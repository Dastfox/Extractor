
import requests
from bs4 import BeautifulSoup
from CRUD import Book, generateCsv

url = ('http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html')

currentItem= Book().generate_data(url)
name = url.replace('http://books.toscrape.com/catalogue/','').replace("/index.html",'')

generateCsv(currentItem, name)

print(f"extracted {len(currentItem)} items from {currentItem.values()}")

import requests
import os
from bs4 import BeautifulSoup
import csv


class Book:
    # generate fields
    def generate_data(self, url):
        itemData = {}
        itemData.update(self.item_url(url))
        itemData.update(self.item_upc_prices_stocks(url))
        itemData.update(self.item_desc_reviews(url))
        itemData.update(self.item_category(url))
        itemData.update(self.item_title(url))
        itemData.update(self.item_img(url))
        return itemData

    # reads data from request
    def get_data(self, url):
        pageContent = requests.get(url).content.decode(
            'utf8').encode('utf8', 'ignore')
        return BeautifulSoup(pageContent, 'lxml')

    def item_url(self, url):
        return {'product_page_url': url}

    def item_upc_prices_stocks(self, url):
        data = self.get_data(url)

        for tr in data.find_all('tr'):
            if 'UPC' in tr.text:
                upc = tr.td.text
            elif 'excl' in tr.text:
                priceExclTax = tr.td.text.replace('Â', '')
            elif 'incl' in tr.text:
                priceInclTax = tr.td.text.replace('Â', '')
            elif 'Availability' in tr.text:
                stock = tr.td.text.split(' ')[3].replace('(', '')
        return {
            'upc': upc,
            'price_excluding_tax': priceExclTax,
            'price_including_tax': priceInclTax,
            'number_available': stock
        }

    def item_desc_reviews(self, url):
        data = self.get_data(url)
        for p in data.find_all('p'):
            try:
                rating = p['class']
                if 'star-rating' in rating:
                    review = rating[1]
            except KeyError:
                desc = p.text
        return {
            'review_rating': review,
            'product_description': desc
        }

    def item_title(self, url):
        data = self.get_data(url)
        return {'title': data.h1.text}

    def item_category(self, url):
        data = self.get_data(url)
        for a in data.ul.find_all('a'):
            if 'Home' not in a.text and 'Books' not in a.text:
                return {'category': a.text}

    def item_img(self, url):
        data = self.get_data(url)
        imageUrl = data.img['src'].replace(
            '../..', 'http://books.toscrape.com')
        image = requests.get(imageUrl)
        category = self.item_category(url)
        title = self.item_title(url)
        path = 'data/' + category['category'] + '/imgs'
        imageTitle = ''.join(
            [x for x in title['title'] if x.isalnum()]) + '.jpg'
        if not os.path.exists(path):
            os.makedirs(path)
        open(f'{path}/{imageTitle}', 'wb').write(image.content)
        return {'image_url': imageUrl, 'image_path': f'{path}/{imageTitle}'}


# csv generation
def generateCsv(itemList):
    columns = ['product_page_url', 'upc', 'title', 'price_including_tax', 'price_excluding_tax',
               'number_available', 'product_description', 'category', 'review_rating', 'image_url', 'image_path']

    category = itemList[0]['category']
    csvFile = f'{category}.csv'

    with open(f'./data/{category}/{csvFile}', 'w', errors='replace') as csvFile:
        file = csv.DictWriter(csvFile, delimiter=";", fieldnames=columns)
        file.writeheader()
        for data in itemList:
            file.writerow(data)

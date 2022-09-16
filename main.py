
import requests
from bs4 import BeautifulSoup
from CRUD import Book, generateCsv

pageContent = requests.get('http://books.toscrape.com/index.html')
actualPage = BeautifulSoup(pageContent.text, 'lxml')

print('type "all" to get evry category or "one" get only one')


inputOneAll = input()
categories = {}
categoriesToPrint = {}

if inputOneAll != 'all':  # if you wanna fetch one
    # finds categories & suscribes keys
    for a in actualPage.find('div', {'class': 'side_categories'}).ul.find_all('a'):
        if 'books_1' not in a.get('href'):
            categoriesToPrint[a.text.replace(
                '\n', '').replace('  ', '')] = a.get('href')
    listOfKeys = list(categoriesToPrint.keys())
    for i in listOfKeys:
        print(i)
    print('Entrer la catégorie désirée parmi celles ci-dessus')
    categoryKey = input()
    if categoryKey not in listOfKeys:
        print('Aucune catégorie portant ce nom')
        quit()
    else:
        categoryUrlEnd = categoriesToPrint[categoryKey]
        print(
            f'Vous voulez les livres de\n "http://books.toscrape.com/{categoryUrlEnd}"?\n (y/n)')
        inputYn = input()
        if inputYn == 'y':
            categories[categoryKey] = f'http://books.toscrape.com/{categoryUrlEnd}'
        else:
            print("Fermeture du script")
            quit()

else:  # if you wanna fetch all

    print(f'Vous voulez les livres de\n "http://books.toscrape.com/catalogue.html"?\n (y/n)')
    inputYn = input()
    if inputYn == 'y':
        for a in actualPage.find('div', {'class': 'side_categories'}).ul.find_all('a'):
            if 'books_1' not in a.get('href'):
                categories[a.text.replace('\n', '').replace(
                    '  ', '')] = f'http://books.toscrape.com/{a.get("href")}'
                categoryKey = list(categories.keys())
    else:
        print("Fermeture du script")
        quit()

# gets data from items in category
for categories, catUrl in categories.items():
    print(f'extrating from {categories}')
    pageContent = requests.get(catUrl)
    actualPage = BeautifulSoup(pageContent.text, 'lxml')

    # category> number of pages
    if actualPage.find('ul', {'class': 'pager'}):
        numberOfPageinCategory = int(actualPage.find(
            'li', {'class': 'current'}).text.replace(' ', '').split('of')[1])
    else:
        numberOfPageinCategory = 1
# récupération des urls de chaque livre présent dans la catégorie
    targetUrls = []
    for pages in range(1, numberOfPageinCategory + 1):
        for item in actualPage.find_all('article'):
            url: str = 'http://books.toscrape.com/catalogue/' + \
                item.h3.a.get("href").replace("../../../", '')
            targetUrls.append(url)
        if numberOfPageinCategory > 1:
            nextPage = requests.get(catUrl.replace(
                'index.html', f'page-{str(pages + 1)}.html'))

            actualPage = BeautifulSoup(nextPage.text, 'lxml')

    # Gets the info of evry item in range
    allItemInRange = []
    for url in targetUrls:
        currentItem = Book().generate_data(url)
        allItemInRange.append(currentItem)

    # Ecriture des fichiers CSV
    generateCsv(allItemInRange)

    print(f"extracted {len(allItemInRange)} items from {categories}")

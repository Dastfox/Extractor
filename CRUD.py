import requests
import os
from bs4 import BeautifulSoup
import csv


class Book:
    # generate fields calling evry fonction that gives target's data
    # this called func return a kwarg {"key:coloumn name" : value}
    def generate_data(self, url):
        itemData = {}
        itemData.update(self.item_url(url))
        itemData.update(self.item_upc_prices_stocks(url))
        itemData.update(self.item_description_and_reviews(url))
        itemData.update(self.item_category(url))
        itemData.update(self.item_title(url))
        itemData.update(self.item_image(url))
        return itemData

    # reads data from request: this function is used in functions below
    # returns the content (lxml toolkit used for processing html)
    def get_data(self, url):
        pageContent = requests.get(url).content.decode("utf8").encode("utf8", "ignore")
        return BeautifulSoup(pageContent, "lxml")

    # returns the url already stocked in item though his key
    def item_url(self, url):
        return {"product_page_url": url}

    # Gets: upc, price_excluding_tax, price_including_tax & number_available
    def item_upc_prices_stocks(self, url):
        # gets data using request & BS
        data = self.get_data(url)

        # scraps "tr" to get all info from bottom page table
        for tr in data.find_all("tr"):
            # td is the subcategory of text containt needed data
            if "UPC" in tr.text:
                upc = tr.td.text
            elif "excl" in tr.text:
                priceExclTax = tr.td.text
            elif "incl" in tr.text:
                priceInclTax = tr.td.text
            # form of the request is "In stock (22 available)" so I split at evry space
            # then i get the third item of "In, stock, (22, available)"
            # then i delete the parenthesis to get only the number replacing "(" with nothing
            elif "Availability" in tr.text:

                stock = tr.td.text.split(" ")[2].replace("(", "")
        return {
            "upc": upc,
            "price_excluding_tax": priceExclTax,
            "price_including_tax": priceInclTax,
            "number_available": stock,
        }

    # here the class contains the data we need to get review stars number
    # in the books pages the only <p> that have ne class is description so this
    # function looks for classes to get the star review, if the object has no class
    # its the description so I put it in a decription variable
    def item_description_and_reviews(self, url):
        # empty des cription security
        description = ""
        data = self.get_data(url)
        for p in data.find_all("p"):
            try:
                # gets classes of all <p> that have classes in rating variable
                classes_of_p_that_have_class = p["class"]
                # gets the 2nd class of the <p> that have the class .star-rating
                # because the request looks like p.star-rating.Note and i need ".Note" so the 2nd class
                if "star-rating" in classes_of_p_that_have_class:
                    review = classes_of_p_that_have_class[1]
            except KeyError:
                description = p.text
            # if no class: <p> is decription

        return {"review_rating": review, "product_description": description}

    # title is the only <h1> tag so simple scrap
    def item_title(self, url):
        data = self.get_data(url)
        return {"title": data.h1.text}

    # gets all <a> looks for the one that is not a parent index link by excludong "Home" & "Books" from getted data
    # the only data remaining is category
    def item_category(self, url):
        data = self.get_data(url)
        for a in data.ul.find_all("a"):
            if "Home" not in a.text and "Books" not in a.text:
                return {"category": a.text}

    # gets the images and saves it to category> imgs > scrapped book name
    def item_image(self, url):
        data = self.get_data(url)
        # replaces image src relative path with absolute path to get to it saves it to "imageUrl"
        imageUrl = data.img["src"].replace("../..", "http://books.toscrape.com")
        # gets a Response from imageUrl
        image = requests.get(imageUrl)
        # gets the category to get to the right folder
        category = self.item_category(url)
        # gets the  scrapped book name in title variable
        title = self.item_title(url)
        # concats data : folder wich contains all scrappen data / category getted below / images : folder where we want images
        path = "data/" + category["category"] + "/images"
        # concats the title to remove spaces & char that are not alpha numeric chars & .jpg so its well saved with a format
        imageTitle = "".join([x for x in title["title"] if x.isalnum()]) + ".jpg"
        # creates the directory if it doesn't exists
        if not os.path.exists(path):
            os.makedirs(path)
        # opens the image in "write and binary" mode (wb), write its content
        open(f"{path}/{imageTitle}", "wb").write(image.content)
        # returns image url & its path in data architecture
        return {"image_url": imageUrl, "image_path": f"{path}/{imageTitle}"}


# csv generation
def generateCsv(itemList):
    # list used to right colums at the top of the csv
    columns = [
        "product_page_url",
        "upc",
        "title",
        "price_including_tax",
        "price_excluding_tax",
        "number_available",
        "product_description",
        "category",
        "review_rating",
        "image_url",
        "image_path",
    ]
    # puts category in a path to use it as a location info
    category = itemList[0]["category"]
    # puts the filename in a var to create it properly
    csvFile = f"{category}.csv"

    # opens the right file as a csv
    with open(f"./data/{category}/{csvFile}", "w", errors="replace") as csvFile:
        # writes rows
        file = csv.DictWriter(csvFile, delimiter=";", fieldnames=columns)
        file.writeheader()
        for data in itemList:
            # write evry data from actual object
            file.writerow(data)

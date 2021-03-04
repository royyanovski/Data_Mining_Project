import sys
import requests  # A package for downloading HTML code from a website.
from bs4 import BeautifulSoup  # A package for parsing HTML code.
import argparse
import json

CFG_FILE = "/Users/royyanovski/data_mining_proj/config_filw.json"
with open(CFG_FILE, 'r') as cf:
    config = json.load(cf)

CON = config["constants"]
TAG = config["tags"]
URL_PATTERN = config["url_address_pattern"]


def get_data(link_list):
    """
    Receives a list of links to product pages in ebay and prints
    their: title, price, sending country, shipping fee, and condition.
    """
    for link in link_list:
        item_page = requests.get(link)
        item_soup = BeautifulSoup(item_page.content, 'html.parser')
        item_results = item_soup.find(id="Body")
        title_elem = item_results.find(TAG["title_tag"], class_=TAG["title_class"])
        price_elem = item_results.find(TAG["price_tag"], id=TAG["price_id"])
        location_elem = item_results.find(TAG["location_tag"], class_=TAG["location_class"])
        shipment_elem = item_results.find(TAG["shipment_tag"], class_=TAG["shipment_class"])
        freeshipping_elem = item_results.find(TAG["freeship_tag"], class_=TAG["freeship_class"])
        condition_elem = item_results.find(TAG["condition_tag"], class_=TAG["condition_class"])

        title_elem.find(TAG["title_torm_tag"], class_=TAG["title_torm_class"]).decompose()
        if shipment_elem is not None:
            shipment_elem = shipment_elem.contents[CON["PRICE_ONLY"]]
        if price_elem is not None:
            price_elem.contents[CON["TO_DELETE"]].decompose()
        if location_elem is not None and ',' in location_elem.text:
            country_only = item_soup.new_tag('span')
            country_only.string = location_elem.text.strip().split(", ")[CON["COUNTRY"]]
            location_elem = country_only

        chosen_elements = [title_elem, price_elem, location_elem, shipment_elem, freeshipping_elem,  condition_elem]
        for elem in chosen_elements:
            if elem is not None:
                print(elem.text.strip())
        print()


def roys_webscraper(url, no_of_scraped_pages):
    """
    Webscraping function for ebay. Running on a pre-determined number of search pages,
    starting from the entered first search page. Output: prints title, price, supplier country,
    and shipping cost for each item.
    """
    for page_no in range(CON["FIRST_PAGE"], no_of_scraped_pages + CON["FIRST_PAGE"]):
        links = []
        try:
            page = requests.get(url)  # Getting the HTML code.
        except requests.exceptions.MissingSchema:
            print('Invalid URL address.')
            sys.exit()
        else:
            soup = BeautifulSoup(page.content, 'html.parser')  # Creating BS object to work on with an HTML parser.
            results = soup.find(id="mainContent")  # Extracting the results of the ebay search.
            product_items = results.find_all(TAG["each_product_tag"], class_=TAG["each_product_class"])  # Separating
            # and using only the results themselves.
            for product_item in product_items:  # Getting the links for the product pages.
                try:
                    link = product_item.find(TAG["product_link_tag"])[TAG["product_link_class"]]  # Extract item links.
                except (TypeError, KeyError):
                    continue
                else:
                    links.append(link)
            get_data(links)
            url = url[:CON["PAGE_NO"]] + str(page_no)


def main():
    """
    Receives CLI arguments for the ebay web scraper.
    """
    parser = argparse.ArgumentParser(description='Scrapes product data from ebay.')
    parser.add_argument('search_words', type=str, help="products to search for (if the search key is more than one "
                                                       "word, use '_' between words.", nargs='+')
    parser.add_argument('-p', '--pages', type=int, help='number of pages to scrape for each search', default=1)
    args = parser.parse_args()

    for model in args.search_words:
        url_address = URL_PATTERN.format(model)
        roys_webscraper(url_address, args.pages)


if __name__ == "__main__":
    main()

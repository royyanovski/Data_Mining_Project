import sys
import requests  # A package for downloading HTML code from a website.
from bs4 import BeautifulSoup  # A package for parsing HTML code.
import argparse
import json
import pymysql.cursors


CFG_FILE = "/Users/royyanovski/data_mining_proj/config_filw.json"
with open(CFG_FILE, 'r') as cf:
    config = json.load(cf)
PASS_FILE = "/Users/royyanovski/mypass.json"
with open(PASS_FILE, 'r') as pf:
    password = json.load(pf)

MY_PASSWORD = password["my_password"]
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
        category_elem = item_results.find(TAG["category_tag"], itemprop=TAG["category_itemprop"])
        seller_elem = item_results.find(TAG["seller_tag"], class_=TAG["seller_class"])
        seller_link = seller_elem.find(TAG["link_tag"])[TAG["link_class"]]

        title_elem.find(TAG["title_torm_tag"], class_=TAG["title_torm_class"]).decompose()
        if shipment_elem is not None:
            shipment_elem = shipment_elem.contents[CON["PRICE_ONLY"]]
        if price_elem is not None:
            price_elem.contents[CON["TO_DELETE"]].decompose()
        if location_elem is not None and ',' in location_elem.text:
            country_only = item_soup.new_tag('span')
            country_only.string = location_elem.text.strip().split(", ")[CON["COUNTRY"]]
            location_elem = country_only

        seller_page = requests.get(seller_link)
        seller_soup = BeautifulSoup(seller_page.content, 'html.parser')
        seller_results = seller_soup.find('body')
        seller_name = item_results.find(TAG["sel_name_tag"], class_=TAG["sel_name_class"])
        posit_feed_pct = seller_results.find(TAG["pos_pct_tag"], class_=TAG["pos_pct_class"])
        feedback_score = item_results.find(TAG["score_tag"], class_=TAG["score_class"])
        clean_feedback_score = feedback_score.text.strip().replace(')', '').replace('(', '')

        chosen_elements = [title_elem, price_elem, location_elem, shipment_elem, freeshipping_elem,  condition_elem, category_elem]
        seller_elements = [seller_name, posit_feed_pct]
        for elem in chosen_elements:
            if elem is not None:
                print(elem.text.strip())
        print()
        print('Seller:')
        for elem in seller_elements:
            if elem is not None:
                print(elem.text.strip())
        print(clean_feedback_score)
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
                    link = product_item.find(TAG["link_tag"])[TAG["link_class"]]  # Extract item links.
                except (TypeError, KeyError):
                    continue
                else:
                    links.append(link)
            get_data(links)
            url = url[:CON["PAGE_NO"]] + str(page_no)


def storing_data(chosen_elements_list, seller_elements_list, feedback_score):
    prod_name = chosen_elements_list[0].text.strip()
    price = float(chosen_elements_list[1].text.strip().split(' ')[1])
    country = chosen_elements_list[2].text.strip()
    if chosen_elements_list[3].text.strip() == 'FREE':
        ship_cost = 0.0
    else:
        ship_cost = float(chosen_elements_list[3].text.strip().split(' ')[1])
    condition = chosen_elements_list[4].text.strip()
    category = chosen_elements_list[5].text.strip()
    sell_name = seller_elements_list[0].text.strip()
    pos_pct = float(seller_elements_list[1].text.strip().split('%')[0])

    insert_to_products_query = f"""INSERT INTO products (product_name, product_price, origin_country, 
    shipping_fee, product_condition) VALUES ({prod_name}, {price}, {country}, {ship_cost}, {condition});"""

    insert_to_categories_query = f"""INSERT INTO categories (category) VALUES ({category});"""

    insert_to_sellers_query = f"""INSERT INTO sellers (seller_name, pos_feedback_pct, seller_feedback_score) 
    VALUES ({sell_name}, {pos_pct}, {int(feedback_score)});"""

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password=MY_PASSWORD,
                                 database='ebay_products',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    with connection.cursor() as cursor:
        cursor.execute(insert_to_products_query + insert_to_categories_query + insert_to_sellers_query)
        connection.commit()


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

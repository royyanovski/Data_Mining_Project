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


def get_item_data(item_link):
    item_page = requests.get(item_link)
    item_soup = BeautifulSoup(item_page.content, 'html.parser')
    item_results = item_soup.find(id="Body")
    title_elem = item_results.find(TAG["title_tag"], class_=TAG["title_class"])
    price_elem = item_results.find(TAG["price_tag"], id=TAG["price_id"])
    location_elem = item_results.find(TAG["location_tag"], class_=TAG["location_class"])
    shipment_elem = item_results.find(TAG["shipment_tag"], class_=TAG["shipment_class"])
    freeshipping_elem = item_results.find(TAG["freeship_tag"], class_=TAG["freeship_class"])
    condition_elem = item_results.find(TAG["condition_tag"], class_=TAG["condition_class"])
    category_elem = item_results.find(TAG["category_tag"], itemprop=TAG["category_itemprop"])

    seller_name = item_results.find(TAG["sel_name_tag"], class_=TAG["sel_name_class"])
    feedback_score = item_results.find(TAG["score_tag"], class_=TAG["score_class"])
    clean_feedback_score = feedback_score.text.strip().replace(')', '').replace('(', '')

    title_elem.find(TAG["title_torm_tag"], class_=TAG["title_torm_class"]).decompose()
    if shipment_elem is not None:
        shipment_elem = shipment_elem.contents[CON["PRICE_ONLY"]]
    if price_elem is not None:
        price_elem.contents[CON["TO_DELETE"]].decompose()
    if location_elem is not None and ',' in location_elem.text:
        country_only = item_soup.new_tag('span')
        country_only.string = location_elem.text.strip().split(", ")[CON["COUNTRY"]]
        location_elem = country_only

    chosen_elements = [title_elem, price_elem, location_elem, shipment_elem, freeshipping_elem, condition_elem,
                       category_elem]
    return chosen_elements, seller_name, clean_feedback_score


def concentrating_data(link_list):
    """
    Receives a list of links to product pages in ebay and prints
    their: title, price, sending country, shipping fee, and condition.
    """
    for link in link_list:
        prod_data_and_sell_link = get_item_data(link)
        product_data = prod_data_and_sell_link[0]
        seller_name = prod_data_and_sell_link[1]
        seller_score = prod_data_and_sell_link[2]

        for elem in product_data:
            if elem is not None:
                print(elem.text.strip())
        print()
        print('Seller:')
        print(seller_name.text.strip())
        print(seller_score)
        print()


def collect_links(product_items):
    links = []
    for product_item in product_items:
        try:
            link = product_item.find(TAG["link_tag"])[TAG["link_class"]]
        except (TypeError, KeyError):
            continue
        else:
            links.append(link)
    return links


def roys_webscraper(url, no_of_scraped_pages):
    """
    Webscraping function for ebay. Running on a pre-determined number of search pages,
    starting from the entered first search page. Output: prints title, price, supplier country,
    and shipping cost for each item.
    """
    for page_no in range(CON["FIRST_PAGE"], no_of_scraped_pages + CON["FIRST_PAGE"]):
        try:
            page = requests.get(url)
        except requests.exceptions.MissingSchema:
            print('Invalid URL address.')
            sys.exit()
        else:
            soup = BeautifulSoup(page.content, 'html.parser')
            results = soup.find(id="mainContent")
            product_items = results.find_all(TAG["each_product_tag"], class_=TAG["each_product_class"])
            links = collect_links(product_items)
            concentrating_data(links)
            url = url[:CON["PAGE_NO"]] + str(page_no)


def sql_execution(prod_name, price, country, ship_cost, condition, category, seller_name, feedback_score):
    insert_to_products_query = f"""INSERT INTO products (product_name, product_price, origin_country, 
        shipping_fee, product_condition) VALUES ({prod_name}, {price}, {country}, {ship_cost}, {condition})
        WHERE NOT EXISTS (SELECT product_name, product_price, origin_country FROM products WHERE 
        product_name = prod_name AND product_price = price AND origin_country = country);"""

    get_item_id_query = f"""SELECT * FROM products WHERE 
        product_name = prod_name AND product_price = price AND origin_country = country"""

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password=MY_PASSWORD,
                                 database='ebay_products',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        cursor.execute(insert_to_products_query)
        connection.commit()

    with connection.cursor() as cursor:
        cursor.execute(get_item_id_query)
        result = cursor.fetchall()
        prod_id = result['product_id']
        connection.commit()

    insert_to_categories_query = f"""INSERT INTO categories (product_id, category) VALUES ({prod_id}, {category})
        WHERE NOT EXISTS (SELECT product_id FROM categories WHERE product_id = prod_id);"""

    insert_to_sellers_query = f"""INSERT INTO sellers (product_id, seller_name, pos_feedback_pct, seller_feedback_score) 
        VALUES ({prod_id}, {seller_name}, {int(feedback_score)})
        WHERE NOT EXISTS (SELECT product_id FROM sellers WHERE product_id = prod_id);"""

    with connection.cursor() as cursor:
        cursor.execute(insert_to_categories_query + insert_to_sellers_query)
        connection.commit()

    connection.close()


def storing_data(chosen_elements_list, sell_name, feedback_score):
    prod_name = chosen_elements_list[CON["NAME_ELEM"]].text.strip()
    price = float(chosen_elements_list[CON["PRICE_ELEM"]].text.strip().split(' ')[CON["PRICE_ONLY"]])
    country = chosen_elements_list[CON["COUNTRY_ELEM"]].text.strip()
    if chosen_elements_list[CON["SHIPMENT_ELEM"]].text.strip() == 'FREE':
        ship_cost = 0.0
    else:
        ship_cost = float(chosen_elements_list[3].text.strip().split(' ')[CON["PRICE_ONLY"]])
    condition = chosen_elements_list[CON["CONDITION_ELEM"]].text.strip()
    category = chosen_elements_list[CON["CATEGORY_ELEM"]].text.strip()
    seller_name = sell_name.text.strip()

    sql_execution(prod_name, price, country, ship_cost, condition, category, seller_name, feedback_score)


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
        if '_' in model:
            model = " ".join(model.split('_'))
        url_address = URL_PATTERN.format(model)
        roys_webscraper(url_address, args.pages)


if __name__ == "__main__":
    main()

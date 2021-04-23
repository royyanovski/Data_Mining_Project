import sys
import requests
from bs4 import BeautifulSoup
import argparse
import json
import pymysql.cursors
import logging

CFG_FILE = "/Users/royyanovski/data_mining_proj/config_file.json"
with open(CFG_FILE, 'r') as cf:
    config = json.load(cf)
PASS_FILE = "/Users/royyanovski/mypass.json"
with open(PASS_FILE, 'r') as pf:
    passwords = json.load(pf)

MY_PASSWORD = passwords["my_password"]
URLS = config["urls"]
CON = config["constants"]
TAG = config["tags"]
QUE = config["queries"]
URL_PATTERN = URLS["url_address_pattern"]
API_URL = URLS["api_url"]
API_HEADERS = passwords["api_headers"]

logging.basicConfig(filename='ebay_scraping.log', format='%(asctime)s - %(levelname)s - FILE:%(filename)s - FUNC:%('
                                                         'funcName)s - LINE: %(lineno)d - %(message)s',
                    level=logging.WARNING)

# Currency API:
response = requests.request("GET", API_URL, headers=API_HEADERS)
api_check = response
if api_check.status_code != CON["SUCCESS"]:
    logging.error(f"Could not connect to the API. Status code: {api_check.status_code}.")
else:
    logging.info('API was successfully accessed')
    conversion_dict = response.json()


def sql_execution(prod_name, price, country, ship_cost, condition, prod_category, page_no, sell_name, feedback_score,
                  cur_elem):
    """
    Executes SQL queries in order to insert product data into a database.
    """

    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password=MY_PASSWORD,
                                 database='ebay_products',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    with connection.cursor() as cursor:
        x = 'go'
        query = QUE["get_prod_and_sel_name"]
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            if result['seller_name'] == sell_name and result['product_name'] == prod_name:
                x = 'no_go'
        connection.commit()

    if x == 'go':
        logging.info('No duplicates found.')
        queries = [QUE["insert_to_conditions"] % condition, QUE["insert_to_countries"] % country,
                   QUE["insert_to_categories"] % prod_category, QUE["insert_to_sellers"] % (sell_name, feedback_score)]

        for query in queries:
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)
                except pymysql.err.IntegrityError:
                    logging.warning('Identical value found in unique field. No new entry.')
                else:
                    connection.commit()
        try:
            with connection.cursor() as cursor:
                query = QUE["get_seller_id"] % sell_name
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    seller_id = result['seller_id']
                connection.commit()

            with connection.cursor() as cursor:
                query = QUE["get_category_id"] % prod_category
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    category_id = result['category_id']
                connection.commit()

            with connection.cursor() as cursor:
                query = QUE["get_country_id"] % country
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    country_id = result['country_id']
                connection.commit()

            with connection.cursor() as cursor:
                query = QUE["get_condition_id"] % condition
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    condition_id = result['condition_id']
                connection.commit()

            with connection.cursor() as cursor:
                query = QUE["insert_to_products"] % (seller_id, category_id, country_id, condition_id, prod_name, price,
                                                     ship_cost, page_no)
                cursor.execute(query)
                connection.commit()

            with connection.cursor() as cursor:
                query = QUE["get_product_id"] % (prod_name, seller_id)
                cursor.execute(query)
                results = cursor.fetchall()
                for result in results:
                    prod_id = result['product_id']
                connection.commit()

            with connection.cursor() as cursor:
                query = QUE["insert_to_currency"] % (
                    prod_id, cur_elem['IL'], cur_elem['US'], cur_elem['EU'], cur_elem['GB'],
                    cur_elem['China'], cur_elem['Russia'])
                cursor.execute(query)
                connection.commit()
        except pymysql.err.ProgrammingError:
            logging.error('A problem occurred while trying to store product details.')
            connection.close()
        else:
            logging.info('A record was successfully stored in db.')
            print('A record was successfully stored in db.')
            connection.close()
    else:
        logging.info('Found a duplicate. Did not perform insert for this record.')
        print('A record was not stored.')


def convert_currency(ils_price):
    """
    Uses an external API to calculate different currencies of the price, provided as input.
    Returns: A dictionary with countries as keys, and the price in their respected currencies.
    """
    logging.debug(f"The is: {ils_price}, entered as type: {type(ils_price)}.")
    convert_to = [('US', 'USD'), ('EU', 'EUR'), ('GB', 'GBP'), ('China', 'CNY'), ('Russia', 'RUB')]
    all_converted = {'IL': ils_price}
    for conv_to in convert_to:
        conv_rate = conversion_dict['rates'][conv_to[CON['CURRENCY']]]
        converted_price = ils_price * conv_rate
        all_converted[conv_to[CON['FROM']]] = converted_price
    return all_converted


def storing_data(chosen_elements_list, sell_name, feedback_score, page_no):
    """
    Stores data in a database.
    """
    prod_name = chosen_elements_list[CON["NAME_ELEM"]]
    if ',' in chosen_elements_list[CON["PRICE_ELEM"]]:
        preprice = "".join(chosen_elements_list[CON["PRICE_ELEM"]].split(','))
        price = float(preprice.split(' ')[CON["PRICE_ONLY"]])
    else:
        price = float(chosen_elements_list[CON["PRICE_ELEM"]].split(' ')[CON["PRICE_ONLY"]])
    country = chosen_elements_list[CON["COUNTRY_ELEM"]]
    if chosen_elements_list[CON["SHIPMENT_ELEM"]] != 0.0 and ',' in chosen_elements_list[CON["SHIPMENT_ELEM"]]:
        preship = "".join(chosen_elements_list[CON["SHIPMENT_ELEM"]].split(','))
        ship_cost = float(preship.split(' ')[CON["PRICE_ONLY"]])
    elif chosen_elements_list[CON["SHIPMENT_ELEM"]] != 0.0:
        ship_cost = float(chosen_elements_list[CON["SHIPMENT_ELEM"]].split(' ')[CON["PRICE_ONLY"]])
    else:
        ship_cost = 0.0
    condition = chosen_elements_list[CON["CONDITION_ELEM"]].text.strip()
    category = chosen_elements_list[CON["CATEGORY_ELEM"]].text.strip()
    seller_name = sell_name.text.strip()
    currency_elements = convert_currency(price + ship_cost)
    logging.info('Ready to store record via SQL')

    sql_execution(prod_name, price, country, ship_cost, condition, category, page_no, seller_name, feedback_score,
                  currency_elements)


def element_parsing(title_elem, price_elem, location_elem, condition_elem, category_elem, seller_name, feedback_score,
                    shipment_elem, freeshipping_elem, item_soup):
    """
    Gets all the scraped elements and parse them.
    """
    feedback_score = int(feedback_score.text.strip().replace(')', '').replace('(', ''))
    logging.info('Feedback score retrieved.')
    title_elem.find(TAG["title_torm_tag"], class_=TAG["title_torm_class"]).decompose()
    title_elem = title_elem.text.strip()
    logging.info('Item title retrieved.')
    if shipment_elem is not None:
        shipment_elem = shipment_elem.contents[CON["PRICE_ONLY"]]
        shipment_elem = shipment_elem.text.strip()
        logging.info('Shipment price retrieved.')
    if freeshipping_elem is not None and freeshipping_elem.text.strip() == 'FREE':
        shipment_elem = 0.0
    price_elem.contents[CON["TO_DELETE"]].decompose()
    price_elem = price_elem.text.strip()
    logging.info('Item price retrieved.')
    if ',' in location_elem.text:
        country_only = item_soup.new_tag('span')
        country_only.string = location_elem.text.strip().split(", ")[CON["COUNTRY"]]
        location_elem = country_only.text.strip()
        logging.info('Origin country retrieved.')
    else:
        location_elem = location_elem.text.strip()
        logging.info('Origin country retrieved.')

    chosen_elements = [title_elem, price_elem, location_elem, shipment_elem, condition_elem,
                       category_elem]

    return chosen_elements, seller_name, feedback_score


def get_item_data(item_link):
    """
    Receives a link to an item page and returns the collected data.
    """
    logging.debug(f"The item page link is: {item_link}")
    try:
        item_page = requests.get(item_link)
    except requests.exceptions.MissingSchema:
        logging.critical("Invalid item page link")
        print('Invalid item page link address.')
        sys.exit()
    else:
        logging.info('Item page was successfully accessed')
        item_soup = BeautifulSoup(item_page.content, 'html.parser')
        item_results = item_soup.find(id="Body")
        if item_results is not None:
            title_elem = item_results.find(TAG["title_tag"], class_=TAG["title_class"])
            price_elem = item_results.find(TAG["price_tag"], id=TAG["price_id"])
            if price_elem is None:
                price_elem = item_results.find(TAG["price_tag"], id=TAG["price_id2"])
            location_elem = item_results.find(TAG["location_tag"], class_=TAG["location_class"])
            shipment_elem = item_results.find(TAG["shipment_tag"], class_=TAG["shipment_class"])
            freeshipping_elem = item_results.find(TAG["freeship_tag"], class_=TAG["freeship_class"])
            condition_elem = item_results.find(TAG["condition_tag"], class_=TAG["condition_class"])
            category_elem = item_results.find(TAG["category_tag"], itemprop=TAG["category_itemprop"])

            seller_name = item_results.find(TAG["sel_name_tag"], class_=TAG["sel_name_class"])
            feedback_score = item_results.find(TAG["score_tag"], class_=TAG["score_class"])

            for element in [title_elem, price_elem, location_elem, condition_elem, category_elem, seller_name,
                            feedback_score]:
                if element is None:
                    logging.warning('Missing data for item. Item skipped.')
                    return 'NULL'
            if shipment_elem is None and freeshipping_elem is None:
                return 'NULL'
            return element_parsing(title_elem, price_elem, location_elem, condition_elem, category_elem, seller_name,
                                   feedback_score, shipment_elem, freeshipping_elem, item_soup)


def concentrating_data(link_list, page_no):
    """
    Receives a list of links to product pages and the page No., uses a function to retrieve data and
    sends it to a storing function.
    """
    for link in link_list:
        prod_data_and_sell_link = get_item_data(link)
        if prod_data_and_sell_link == 'NULL':
            continue
        try:
            product_data = prod_data_and_sell_link[CON["ITEM_DATA"]]
        except TypeError:
            logging.warning('Problematic link ignored.')
        else:
            seller_name = prod_data_and_sell_link[CON["SELLER_NAME"]]
            seller_score = prod_data_and_sell_link[CON["SELLER_SCORE"]]

            storing_data(product_data, seller_name, seller_score, page_no)


def collect_links(product_items):
    """
      Extract item page links and returns a list of links.
      """
    links = []
    for product_item in product_items:
        try:
            link = product_item.find(TAG["link_tag"])[TAG["link_class"]]
        except (TypeError, KeyError):
            logging.warning("Could not find item page link.")
            continue
        else:
            logging.info(f"Found item page link: {link}")
            links.append(link)
    return links


def ebay_access(url, no_of_scraped_pages):
    """
    Webscraping function for ebay. Running on a pre-determined number of search pages,
    starting from the entered first search page. Output: prints title, price, supplier country,
    and shipping cost for each item.
    """
    print('Connecting to ebay...')
    for page_no in range(CON["FIRST_PAGE"], no_of_scraped_pages + CON["FIRST_PAGE"]):
        logging.debug(f'Entered url is: {url}')
        try:
            page = requests.get(url)
        except requests.exceptions.MissingSchema:
            logging.critical("Invalid item page link")
            print('Invalid URL address.')
            sys.exit()
        else:
            logging.info(f"Entered item page.")
            soup = BeautifulSoup(page.content, 'html.parser')
            results = soup.find(id="mainContent")
            if results is not None:
                product_items = results.find_all(TAG["each_product_tag"], class_=TAG["each_product_class"])
                links = collect_links(product_items)
                concentrating_data(links, page_no - 1)
                url = url[:CON["PAGE_NO"]] + str(page_no)


class ScrapeIt:
    def __init__(self, search_words, no_of_pages):
        """
        Initiates a new scraping search, by key words and No. of pages entered through the CLI.
        """
        self.search_words = search_words
        self.no_of_pages = no_of_pages

    def scrape_away(self):
        """
        Starts the scraping process for a specific search.
        """
        for search_key in self.search_words:
            if '_' in search_key:
                search_key = " ".join(search_key.split('_'))
            logging.debug(f'The key search word/s is/are: {search_key}')
            url_address = URL_PATTERN.format(search_key)
            logging.debug(f'The main URL is: {url_address}')
            ebay_access(url_address, self.no_of_pages)


def main():
    """
    Receives CLI arguments for the ebay web scraper.
    """
    parser = argparse.ArgumentParser(description='Scrapes product data from ebay.')
    parser.add_argument('search_words', type=str, help="products to search for (if the search key is more than one "
                                                       "word, use '_' between words.", nargs='+')
    parser.add_argument('-p', '--pages', type=int, help='number of pages to scrape for each search', default=1)
    args = parser.parse_args()

    logging.debug(f'The entered arguments are {args.search_words} as key search words, and {args.pages} as the No. of '
                  f'pages to search.')

    new_search = ScrapeIt(args.search_words, args.pages)
    new_search.scrape_away()


if __name__ == "__main__":
    main()

# Data Mining Project
This is a repo for the data mining project of the ITC data science course.

## Description
The aim of this project is to extract data from ebay and analyze it.
The scraper receives CLI arguments.

Input: 
1) search words (str)- enter words to search separated by a whitespace (enters the script as a list).
If a search key is more than one word, use "_" between them.
2) -p/--pages flag (int)- enter the number of pages you would like to search through, for each of the search words.
Input pattern: $ python WebScraping.py search_key1 search_key2 ... -p page_num

Output: The program stores the following in a database, for each search word: product category, product title, category, condition,
price, supplier's country, search page No., shipping cost, and condition, seller name, seller feedback score.
The prices can be found in different currencies, converted by an up-to-date API ('ExchangeRate-API' from 'rapidapi.com').

* As mentioned, the program stores the data in a pre-defined database (named 'ebay_products'), with the following structure:
![ERD](https://github.com/royyanovski/Data_Mining_Project/blob/master/Data%20Mining%20Project.png?raw=true)
(SQL script for DB creation can also be found in this repo)

__Tables details:__
* __products table__- includes individual product data. 
Columns:
  1. _product_id (int, pk)_: auto increments a serial no. for each product.
  2. _seller_id (int, fk)_: ID of seller.
  3. _category_id (int, fk)_: ID of category.
  4. _country_id (int, fk)_: ID of country.
  5. _condition_id (int, fk)_: ID of condition.
  6. _product_name (varchar)_: the title of the product as appears on ebay.
  7. _product_price (float)_: the price of the product, shipping unincluded, in ILS.  
  8. _shipping_fee (float)_: the price of shipping the product in ILS.
  9. _page_number (int)_: the No. of search page in ebay.

* __conditions table__- product conditions. 
Columns:
  1. _condition_id (int, pk)_: ID of condition. 
  2. _product_condition (varchar)_: the condition category of the product (new, open box, seller refurbished, certified
refurbished, used, for parts or not working).

* __countries table__- product conditions. 
Columns:
  1. _country_id (int, pk)_: ID of country.
  2. _origin_country (varchar)_: the country which the product is sent from.

* __categories table__- includes products and the ebay categories which they are related to. 
Columns:
  1. _product_id (int, fk)_: the serial product id.
  2. _category (varchar)_: the products categories.

* __sellers table__- includes seller details per each product. 
Columns:
  1. _seller_id (int, pk)_: ID of seller.
  2. _seller_name (varchar)_: the ebay name of the seller.
  3. _seller_feedback_score (int)_: the score of the seller by ebay's formula.

* __currency table__- prices of products+shipping in different currencies. 
Columns:
  1. _product_id (int, fk)_: the serial product id.
  2. _Israeli_Shekel_ILS_: Price in Israeli Shekels.
  3. _US_Dollar_USD_: Price in US dollars. 
  4. _EU_Euro_EUR_: Price in Euros.
  5. _GB_Pound_GBP_: Price in British Pound.
  6. _China_Yoan_: Price in Chinese Yoan.
  7. _Russia_Ruble_: Price in Russian Ruble.
  
## Installation
This repo includes a requirements file for necessary packages.
In addition, a configuration file includes all constants, tags, and the URL pattern. 
In 'WebScraping.py', rows 9 and 12 include paths to the configuration file (CFG_FILE) and the password file (PASS_FILE)
containing the personal password for the SQL execution, and for the API access from the RapidAPI site.
The paths of these two files should be changed according to their location in the local PC, and personal passwords
should have keys as follows: SQL password: 'my_password', rapidapi password: 'api_headers' as a dictionary with the two
keys received by the website ("x-rapidapi-key" and "x-rapidapi-host").
The program includes logging to a logging file named 'ebay_scraping.log'. The logging level is set to 'warning' but can
be changed in case needed (in line 23 of 'WebScraping.py').

## Usage
WebScraping.py - Receives a list of search words and a number of pages to search (during each search),
and returns the data of all the results (products). The data returned are: product description, price, condition,
shipping fee, product category, seller country, seller name, and seller rating score.

There are 7 functions in the program and 1 main function, calling each other in the following order: 
1. main => 2. ebay_access (=>  3. collect_links) => 4. concentrating_data => 5. get_item_data => 6. storing_data (=>  7. convert_currency) => 8. sql_execution  
                                                   
## Authors and Support
Roy Yanovski - yanovskir@gmail.com

## Project status
Project Completed.

Last Update: 30.03.2021.
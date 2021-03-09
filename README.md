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

Output: The program prints out the following for each search word: product category, product title, price, supplier's country,
shipping cost, and condition, seller name, seller feedback score, and seller positive feedback percentage.
All prices are in Israeli Shekels (i.e. NIS or ILS).
* The program can also store the data in a pre-defined database, as such:
![ERD](/Users/royyanovski/data_mining_proj/Data Mining Project.png)
* __products table__- includes individual product data. 
Columns:
  1. _product_id (int, pk)_: auto increments a serial no. for each product.
  2. _product_name (varchar)_: the title of the product as appears on ebay.
  3. _product_price (float)_: the price of the product, shipping unincluded, in ILS.
  4. _origin_country (varcher)_: the country which the product is sent from.
  5. _shipping_fee (float)_: the price of shipping the product in ILS.
  6. _product_condition (varchar)_: the condition category of the product (new, open box, seller refurbished, certified
refurbished, used, for parts or not working).

* __categories table__- includes products and the ebay categories which they are related to. 
Columns:
  1. _product_id (int, fk)_: the serial product id.
  2. _category (varchar)_: the products categories.

* __sellers table__- includes seller details per each product. 
Columns:
  1. _product_id (int, fk)_: the serial product id.
  2. _seller_name (varchar)_: the ebay name of the seller.
  3. _pos_feedback_pct (float)_: the relative percentage of positive feedbacks, out of all the seller's feedbacks. 
  4. _seller_feedback_score (int)_: the score of the seller by ebay's formula.

## Installation
This repo includes a requirements file for necessary packages.
In addition, a configuration file includes all constants, tags, and the URL pattern. 

## Usage
WebScraping.py - Receives a list of search words and a number of pages to search (during each search),
and returns the data of all the results (products). The data returned are: product description, price, condition,
shipping fee, and seller country.

## Authors and Support
Roy Yanovski - yanovskir@gmail.com

## Project status
Project still in development.
# Data Mining Project
This is a repo for the data mining project of the ITC data science course.

## Description
The aim of this project is to extract data from ebay and analyze it.
The scraper receives CLI arguments.

Input: 
1) search words (str)- enter words to search separated by a whitespace (enters the script as a list).
If a search key is more than one word, use "_" between them.
2) -p/--pages flag (int)- enter the number of pages you would like to search through, for each of the search words.
Input pattern: $ python3 WebScraping.py search_key1 search_key2 ... -p page_num

Output: The program prints out the following for each search word: product title, price, supplier's country,
shipping cost, and condition.
All prices are in Israeli Shekels (i.e. NIS or ILS).

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
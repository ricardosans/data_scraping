"""
Import libraries
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import requests
import random
import time
import os
import re

# Data path
write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/carrefour/'

if os.path.exists(write_path + 'carrefour_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet'):
    exit()

time.sleep(60)
print("\n------Starting------\n")

"""
Parameters and settings
"""
header = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'}
write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/dia/'
# Browsing settings
options = Options()
options.add_argument('--headless')
options.add_argument("--window-size=1920x1080")
# Driver settings
driver_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(options=options)
driver.get('https://www.dia.es/compra-online/')

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
CODE 
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
dictionary = dict(id=list(),
                  category=list(),
                  section_1=list(),
                  section_2=list(),
                  name=list(),
                  brand=list(),
                  price_original=list(),
                  price_final=list(),
                  price_x_unit_or=list(),
                  price_x_unit_fin=list(),
                  unit=list(),
                  special_offer=list(),
                  link=list(),
                  timestamp=list())

# Get the start time for execution duration
st = time.time()

"""
Preparatory functions
"""


def section_2(product_link):
    if product_link[4] != 'p':
        return product_link[4].replace('-', ' ')
    else:
        return None


def exists(data):
    try:
        return data.text.strip()
    except:
        return None


def price_function(price_strings):
    price_strings.reverse()
    prices = []
    for price in price_strings:
        prices.append(float(price.replace('.', '').replace(',', '.')))
    if len(prices) == 2:
        return prices[0], prices[1]
    else:
        return prices[0], None


"""
Main code
"""
time.sleep(2)
# Accept cookies
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'button#onetrust-accept-btn-handler'))) \
    .click()

# Click on hamburger button
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'a.btn-product-catalog'))) \
    .click()

soup = BeautifulSoup(driver.page_source, "lxml")
# Extract urls for all categories
category_urls = soup.find_all('a', class_='go-to-category')
category_urls = [url['href'] for url in category_urls]
# Close driver (won't need it anymore)
driver.quit()
# Iterate over each category
for category in category_urls:
    print(category.split('/')[-2].replace('-', ' '))
    url = requests.get('https://www.dia.es' + category, headers=header).text
    soup = BeautifulSoup(url, "lxml")
    n_pages = int(exists(soup.find('div', class_='pagination-list-and-total')).split(' ')[-1])
    for page in range(0, n_pages):
        url_page = 'https://www.dia.es' + category + '?page={}&disp='.format(page)
        url_page = requests.get(url_page, headers=header).text
        soup_prod = BeautifulSoup(url_page, "lxml")
        soup_prod = soup_prod.find('div', class_='product-list--row')
        products = soup_prod.find_all('div', class_=re.compile('product-list__item'))
        for product in products:
            dictionary['id'].append(product.find('a', class_='productMainLink')['href'].split('/')[-1])
            dictionary['category'].append(category.split('/')[-2].replace('-', ' '))
            dictionary['section_1'].append(product.find('a', class_='productMainLink')['href'].split('/')[3].replace('-', ' '))
            dictionary['section_2'].append(section_2(product.find('a', class_='productMainLink')['href'].split('/')))
            dictionary['name'].append(product.find('a', class_='productMainLink')['title'])
            dictionary['brand'].append(' '.join(re.findall("[A-Z]+", product.find('a', class_='productMainLink')['title'])))
            dictionary['price_original'].append(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='price').text))[1])
            dictionary['price_final'].append(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='price').text))[0])
            dictionary['price_x_unit_or'].append(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='pricePerKilogram').text))[1])
            dictionary['price_x_unit_fin'].append(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='pricePerKilogram').text))[0])
            dictionary['unit'].append(re.findall('[a-zA-Z]+', product.find('p', class_='pricePerKilogram').text)[0])
            dictionary['special_offer'].append(exists(product.find('span', class_='promotion_text')))
            dictionary['link'].append('https://www.dia.es' + product.find('a', class_='productMainLink')['href'])
            dictionary['timestamp'].append(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

            # Here you can add commented prints

        time.sleep(random.randint(0, 2))

# Store and save the data
df = pd.DataFrame(dictionary)
df['category'] = df['category'].astype('category')
df['section_1'] = df['section_1'].astype('category')
df['section_2'] = df['section_2'].astype('category')
df['price_original'] = df['price_original'].astype('float')
df['price_final'] = df['price_final'].astype('float')
df['price_x_unit_or'] = df['price_x_unit_or'].astype('float')
df['price_x_unit_fin'] = df['price_x_unit_fin'].astype('float')
df['unit'] = df['unit'].astype('category')
df['special_offer'] = df['special_offer'].astype('category')
df.to_parquet(write_path + 'dia_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet')

# get the end time
et = time.time()
print('Execution time:', et - st, 'seconds')

# END

"""
            print(product.find('a', class_='productMainLink')['href'].split('/')[-1])
            print(category.split('/')[-2].replace('-', ' '))
            print(product.find('a', class_='productMainLink')['href'].split('/')[3].replace('-', ' '))
            print(section_2(product.find('a', class_='productMainLink')['href'].split('/')))
            print(product.find('a', class_='productMainLink')['title'])
            print(' '.join(re.findall("[A-Z]+", product.find('a', class_='productMainLink')['title'])))
            print(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='price').text))[1])
            print(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='price').text))[0])
            print(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='pricePerKilogram').text))[1])
            print(price_function(re.findall(r'(?:\d+\.)?\d+,\d+', product.find('p', class_='pricePerKilogram').text))[0])
            print(re.findall('[a-zA-Z]+', product.find('p', class_='pricePerKilogram').text)[0])
            print(exists(product.find('span', class_='promotion_text')))
            print('https://www.dia.es' + product.find('a', class_='productMainLink')['href'])
            print(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
            print(page, "\n")
"""

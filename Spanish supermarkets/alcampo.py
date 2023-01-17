"""
Import libraries
"""
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from phantom import setting_webdriver
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import time
import json
import re
import os

# Data path
# write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/eci/'
write_path = '/Users/ricky/Library/CloudStorage/GoogleDrive-ricardo.sans01@alumni.upf.edu/Mi unidad/Ricky/Proyectos personales/Supermercados/BBDD/'

if os.path.exists(write_path + 'alcampo_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet'):
    exit()

# time.sleep(50)
print("\n------Starting------\n")

"""
Parameters
"""
driver = setting_webdriver()
# Browsing settings
driver.set_window_size(1920, 1080)

"""
CODE 
"""
dictionary = dict(id=list(),
                  category=list(),
                  section_1=list(),
                  section_2=list(),
                  section_3=list(),
                  name=list(),
                  brand=list(),
                  price_original=list(),
                  price_final=list(),
                  price_x_unit=list(),
                  unit=list(),
                  link=list(),
                  datestamp=list())

# Get the start time for execution duration
st = time.time()

"""
Preparatory functions
"""
def clean_price(raw_price_x_unit):
    if raw_price_x_unit is not None:
        clean = raw_price_x_unit.text
        clean = clean.replace('(', '').replace(')', '').replace('€', '').split('/')
        clean = float(clean[0].replace('.', '').replace(',', '.')), clean[1].strip()
        return clean
    else:
        return None, None


"""
Main code
"""
driver.get('https://www.alcampo.es/compra-online/')
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'button.cc_b_ok.auxOKButton.cookie-button'))) \
    .click()
time.sleep(100)
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'a.secondary-button.black-secondary'))) \
    .click()
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'input#postalCode'))) \
    .send_keys('08028')

s = requests.Session()
s.headers.update(header)
home_webpage = driver.page_source
soup = BeautifulSoup(home_webpage, 'lxml')
# Extract headers for all categories
category_names = soup.find_all('a', class_='LEVEL_4')
# print(category_names)
category_names = set([category['href'] for category in category_names])
print(category_names)
# print(category_names)
# Iterate over each category
for category in category_names:
    print(category, '\n')
    url = 'https://www.alcampo.es/' + category + '/1'
    webpage = s.get(url).text
    soup = BeautifulSoup(webpage, 'lxml')
    print(soup.prettify())
    # Find number of pages for that category
    n_pages = soup.find(class_=re.compile('pagination-controls'))
    n_pages = int(n_pages.find(id='pagination-current').text.split(' ')[-1])
    # Loop for each page
    for page in range(1, n_pages + 1):
        # Soup for each page
        url = 'https://www.alcampo.es/' + category + '{}/'.format(str(page))
        webpage = s.get(url).text
        soup = BeautifulSoup(webpage, 'lxml')
        # Locate where all products are located within one page
        container = soup.find(class_='c12 js-grid-container')
        # Grasp all jsons from all products
        jsons = container.find_all(attrs={"data-synth": "LOCATOR_PRODUCT_PREVIEW_LIST"})
        # For each json, take the following info:
        for product in jsons:
            # Take the following info for each json
            raw = json.loads(product['data-json'])
            dictionary['id'].append(raw['id'].replace('_', ''))
            dictionary['category'].append(raw['category'][0])
            dictionary['section_1'].append(raw['category'][1])
            dictionary['section_2'].append(raw['category'][2])
            dictionary['section_3'].append(raw['category'][3])
            dictionary['name'].append(raw['name'])
            dictionary['brand'].append(raw.get('brand'))
            dictionary['price_original'].append(raw['price'].get('original'))
            dictionary['price_final'].append(raw['price'].get('final'))
            # For prices per unit
            more_prices = product.find('div', class_='prices-price _pum')
            dictionary['price_x_unit'].append(clean_price(more_prices)[0])
            dictionary['unit'].append(clean_price(more_prices)[1])
            # For link
            more_prices = product.find('a', class_='event js-product-link')['href']
            dictionary['link'].append('https://www.elcorteingles.es' + more_prices)
            dictionary['datestamp'].append(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

        print('Page {} done'.format(str(page)))

df = pd.DataFrame(dictionary)
df['category'] = df['category'].astype('category')
df['section_1'] = df['section_1'].astype('category')
df['section_2'] = df['section_2'].astype('category')
df['section_3'] = df['section_3'].astype('category')
df['price_original'] = df['price_original'].astype('float')
df['price_final'] = df['price_final'].astype('float')
df['price_x_unit'] = df['price_x_unit'].astype('float')
df['unit'] = df['unit'].astype('category')
df.to_parquet(write_path + 'eci_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet')

# get the end time
et = time.time()
print('Execution time:', et - st, 'seconds')

# END

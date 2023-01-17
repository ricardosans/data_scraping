"""
Import libraries
"""
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

if os.path.exists(
        write_path + 'carrefour_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet'):
    exit()

# time.sleep(50)
print("\n------Starting------\n")

"""
Parameters
"""
header = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'}

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


def try_index(data, index):
    try:
        return data[index]
    except:
        print('Returned None for index', index)
        return None


"""
Main code
"""
s = requests.Session()
s.headers.update(header)
home_webpage = s.get('https://www.elcorteingles.es/supermercado/').text
soup = BeautifulSoup(home_webpage, 'lxml')
# Extract headers for all categories
category_names = soup.find_all(class_='top_menu-item js-top-menu-item')
category_names = [section['href'] for section in category_names]
# Iterate over each category
for category in category_names:
    print(category, '\n')
    url = 'https://www.elcorteingles.es' + category + '/1'
    webpage = s.get(url).text
    soup = BeautifulSoup(webpage, 'lxml')
    # Find number of pages for that category
    n_pages = soup.find(class_=re.compile('pagination-controls'))
    n_pages = int(n_pages.find(id='pagination-current').text.split(' ')[-1])
    # Loop for each page
    for page in range(1, n_pages + 1):
        # Soup for each page
        url = 'https://www.elcorteingles.es' + category + '{}/'.format(str(page))
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
            dictionary['category'].append(try_index(raw['category'], 0))
            dictionary['section_1'].append(try_index(raw['category'], 1))
            dictionary['section_2'].append(try_index(raw['category'], 2))
            dictionary['section_3'].append(try_index(raw['category'], 3))
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

# get the end time
et = time.time()
print('Execution time:', et - st, 'seconds')

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

# END

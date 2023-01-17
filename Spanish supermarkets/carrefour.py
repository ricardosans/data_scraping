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
import requests
import datetime
import time
import os

# Data path
# write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/carrefour/'
write_path = '/Users/ricky/Library/CloudStorage/GoogleDrive-ricardo.sans01@alumni.upf.edu/Mi unidad/Ricky/Proyectos personales/Supermercados/BBDD/'

if os.path.exists(write_path + 'carrefour_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet'):
    exit()

# time.sleep(30)
print('\n------Starting------\n')

"""
Parameters
"""
header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36'}
# Browsing settings
options = Options()
# options.add_argument('--headless')
options.add_argument("--disable-extension")
options.add_argument('--disable-blink-features=AutomationControlled')
# Driver settings
driver_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)

"""
CODE 
"""
dictionary = dict(id=list(),
                  category=list(),
                  section_1=list(),
                  section_2=list(),
                  name=list(),
                  price_original=list(),
                  price_final=list(),
                  price_x_unit_or=list(),
                  price_x_unit_fin=list(),
                  unit=list(),
                  special_offer=list(),
                  link=list(),
                  datestamp=list())

# Get the start time for execution duration
st = time.time()

"""
Preparatory functions
"""
def num_pages(input):
    try:
        return int(input.text.strip().split(' ')[-1])
    except:
        return 1

def name_exists(input):
    try:
        return input['alt']
    except:
        return None

def exists(data):
    try:
        return data.text
    except:
        return None

def price_exists(data):
    try:
        return float(data.text.strip().replace(' €', '').replace('.', '').replace(',', '.').split('/')[0])
    except:
        return None


def final_price():
    try:
        price = product.find('span', class_='product-card__price--current').text.strip()
    except:
        price = product.find('span', class_='product-card__price').text.strip()
    price = float(price.replace(' €', '').replace('.', '').replace(',', '.'))
    return price


"""
Main code
"""
s = requests.Session()
s.headers.update(header)
home_webpage = s.get('https://www.carrefour.es/supermercado').text
driver.get('https://www.carrefour.es/supermercado')
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'button#onetrust-reject-all-handler'))) \
    .click()
soup = BeautifulSoup(home_webpage, 'lxml')
# Extract headers for all categories
category_names = soup.find_all('a', class_='nav-first-level-categories__list-element ripple')
category_names = [section['href'] for section in category_names]
# Iterate over each category
for category in category_names[1:]:
    print(category.split('/')[-3].replace('-', ' '))
    url = 'https://www.carrefour.es/supermercado' + category
    webpage = s.get(url).text
    soup = BeautifulSoup(webpage, 'lxml')
    # Access second level of products
    second_cats = soup.find_all('a', 'nav-second-level-categories__list-element ripple')
    second_cats = [section['href'] for section in second_cats]
    for second_cat in second_cats[1:]:
        print('     ' + second_cat.split('/')[-3].replace('-', ' '))
        url = 'https://www.carrefour.es/supermercado' + second_cat
        webpage = s.get(url).text
        soup = BeautifulSoup(webpage, 'lxml')
        # Access second level of products
        third_cats = soup.find_all('a', 'nav-second-level-categories__list-element ripple')
        third_cats = [section['href'] for section in third_cats]
        for third_cat in third_cats:
            print('         ' + third_cat.split('/')[-3].replace('-', ' '))
            url = 'https://www.carrefour.es' + third_cat
            webpage = s.get(url).text
            soup = BeautifulSoup(webpage, 'lxml')
            # Find number of pages for that category
            n_pages = num_pages(soup.find('div', class_='pagination__main'))
            # Loop through each page
            for page in range(0, n_pages):
                # Soup for each page
                url_prod = url + '?offset={}'.format(24 * page)
                driver.get(url_prod)
                try:
                    element = driver.find_element(By.CSS_SELECTOR, 'div.product-card-list__lazy-card')
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                except:
                    pass
                webpage = s.get(url_prod).text
                soup = BeautifulSoup(driver.page_source, 'lxml')
                # Locate where all products are located within one page
                container = soup.find('ul', class_='product-card-list__list')
                # Collect product info from the container
                products = container.find_all('div', class_='product-card')
                # For each product, take the following info:
                for product in products:
                    dictionary['id'].append(product.find('a', class_='product-card__media-link track-click')['href'].split('/')[-2])
                    dictionary['category'].append(category.split('/')[-3].replace('-', ' '))
                    dictionary['section_1'].append(second_cat.split('/')[-3].replace('-', ' '))
                    dictionary['section_2'].append(third_cat.split('/')[-3].replace('-', ' '))
                    dictionary['name'].append(name_exists(product.find('img', class_='product-card__image')))
                    dictionary['price_original'].append(price_exists(product.find('span', class_='product-card__price--strikethrough')))
                    dictionary['price_final'].append(final_price())
                    dictionary['price_x_unit_or'].append(price_exists(product.find('span', class_='product-card__price-per-unit--strikethrough')))
                    dictionary['price_x_unit_fin'].append(float(product.find('span', class_='product-card__price-per-unit').text.strip().replace(' €', '').replace('.', '').replace(',', '.').split('/')[0]))
                    dictionary['unit'].append(product.find('span', class_='product-card__price-per-unit').text.strip().replace(' €', '').replace('.', '').replace(',', '.').split('/')[1])
                    dictionary['special_offer'].append(exists(product.find('span', class_='rm-badge')))
                    dictionary['link'].append('https://www.carrefour.es' + product.find('a', class_='product-card__media-link track-click')['href'])
                    dictionary['datestamp'].append(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

df = pd.DataFrame(dictionary)
# The webpage creates duplicates which we have to remove, thus we sort by reference and take only one row
df = df.sort_values('id').groupby(['id']).first()
df['category'] = df['category'].astype('category')
df['section_1'] = df['section_1'].astype('category')
df['section_2'] = df['section_2'].astype('category')
df['price_original'] = df['price_original'].astype('float')
df['price_final'] = df['price_final'].astype('float')
df['price_x_unit_or'] = df['price_x_unit_or'].astype('float')
df['price_x_unit_fin'] = df['price_x_unit_fin'].astype('float')
df['unit'] = df['unit'].astype('category')
df['special_offer'] = df['special_offer'].astype('category')
df.to_parquet(write_path + 'carrefour_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet')

# get the end time
et = time.time()
print('Execution time:', et - st, 'seconds')

# END

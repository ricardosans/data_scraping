"""
Import libraries
"""
# -*- coding: utf-8 -*-
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import random
import time
import os

# Data path
# write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/carrefour/'
write_path = '/Users/ricky/Library/CloudStorage/GoogleDrive-ricardo.sans01@alumni.upf.edu/Mi unidad/Ricky/Proyectos personales/Supermercados/BBDD/'

# if os.path.exists(write_path + 'carrefour_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet'):
#     exit()

# time.sleep(40)
print("\n------Starting------\n")

"""
Adjusting settings
"""
# Browsing settings
options = Options()
options.add_argument('--headless')
options.add_argument("--disable-extension")
options.add_argument('--disable-blink-features=AutomationControlled')

driver_path = '/usr/local/bin/chromedriver'
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)
driver.get('https://www.mercadona.es/')

write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/mercadona/'


"""
CODE
"""
# Get the start time for execution duration
st = time.time()

"""
Main page
"""

# Accept cookies
WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.ui-button.ui-button--small.ui-button--primary.ui-button--positive')))
WebDriverWait(driver, 50) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'button.ui-button.ui-button--small.ui-button--primary.ui-button--positive'))) \
    .click()


# Add zip code
WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/header/div/div/form/div/input')))
WebDriverWait(driver, 50) \
    .until(EC.element_to_be_clickable((By.XPATH,
                                       '/html/body/div[2]/header/div/div/form/div/input'))) \
    .send_keys('08028')


# Enter the website
WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input.postal-code-form__button')))
WebDriverWait(driver, 50) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'input.postal-code-form__button'))) \
    .click()

"""
Supermarket page
"""
# Click on page where all products are located
WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.menu-item.subhead1-sb')))
WebDriverWait(driver, 20) \
    .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       'a.menu-item.subhead1-sb'))) \
    .click()

time.sleep(5)   # Sleep for 5 seconds (let it load)

## Properties of objects
dictionary = dict(category=list(),
                  section=list(),
                  name=list(),
                  quantity=list(),
                  price=list(),
                  unit=list(),
                  link=list(),
                  datestamp=list())


# Extract page source from the first group of products
WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'span.category-menu__header')))
soup = BeautifulSoup(driver.page_source, "lxml")
macro_sections = soup.find_all('span', class_='category-menu__header')

for section in macro_sections[:]:
    print(section.text)
    WebDriverWait(driver, 20) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           '//label[contains(text(), "' + section.text + '")]'))) \
        .click()
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.category-detail__content')))
    soup = BeautifulSoup(driver.page_source, "lxml")
    sections = soup.find_all('li', class_='subhead1-r category-item')
    category_s = section.text
    section_s = soup.find('li', class_='subhead1-r category-item category-item--selected').text
    soup = soup.find('div', class_='category-detail__content')
    name_s = soup.find_all('h4', class_='subhead1-r product-cell__description-name')
    quantity_s = soup.find_all('div', class_='product-format product-format__size--cell')
    price_s = soup.find_all('p', class_='product-price__unit-price subhead1-b')
    unit_s = soup.find_all('p', class_='product-price__extra-price subhead1-r')
    link_s = soup.find_all('img')

    for product in range(0, len(name_s)):
        dictionary['category'].append(category_s)
        dictionary['section'].append(section_s)
        dictionary['name'].append(name_s[product].text)
        dictionary['quantity'].append(quantity_s[product].text)
        dictionary['price'].append(price_s[product].text.replace(' €', '').replace(',', '.'))
        dictionary['unit'].append(unit_s[product].text.replace('/', '').replace('.', ''))
        dictionary['link'].append(link_s[product]['src'])
        dictionary['datestamp'].append(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

    for micro_sections in sections:
        print('     ' + micro_sections.text)
        WebDriverWait(driver, 20) \
            .until(EC.element_to_be_clickable((By.XPATH,
                                               '//button[contains(text(), "' + str(micro_sections.text) + '")]'))) \
            .click()
        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR,'div.category-detail__content')))
        soup = BeautifulSoup(driver.page_source, "lxml")
        category_s = section.text
        section_s = micro_sections.text
        soup = soup.find('div', class_='category-detail__content')
        name_s = soup.find_all('h4', class_='subhead1-r product-cell__description-name')
        quantity_s = soup.find_all('div', class_='product-format product-format__size--cell')
        price_s = soup.find_all('p', class_='product-price__unit-price subhead1-b')
        unit_s = soup.find_all('p', class_='product-price__extra-price subhead1-r')
        link_s = soup.find_all('img')

        for product in range(0, len(name_s)):
            dictionary['category'].append(category_s)
            dictionary['section'].append(section_s)
            dictionary['name'].append(name_s[product].text)
            dictionary['quantity'].append(quantity_s[product].text)
            dictionary['price'].append(float(price_s[product].text.replace(' €', '').replace(',', '.')))
            dictionary['unit'].append(unit_s[product].text.replace('/', '').replace('.', ''))
            dictionary['link'].append(link_s[product]['src'])
            dictionary['datestamp'].append(datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))

driver.quit()

# get the end time
et = time.time()

# get the execution time
elapsed_time = et - st
print('Execution time:', elapsed_time, 'seconds')

df = pd.DataFrame(dictionary)
df['category'] = df['category'].astype('category')
df['section'] = df['section'].astype('category')
df['price'] = df['price'].astype('float')
df['unit'] = df['unit'].astype('category')
df.to_parquet(write_path + 'mercadona_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet')

# END

"""
Import libraries
"""
# -*- coding: utf-8 -*-
import re

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import random
import time
import os

"""
CODE
"""


def settings():
    # Data path
    # write_path = '/home/schrutebeet/Desktop/Supermercados/BBDD/bonpreuesclat/'
    write_path = '/Users/ricky/Library/CloudStorage/GoogleDrive-ricardo.sans01@alumni.upf.edu/Mi unidad/Ricky/Proyectos personales/Supermercados/BBDD/'

    if os.path.exists(write_path + 'bonpreuesclat_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-',
                                                                                                              '_') + '.parquet'):
        exit()

    print("\n------Starting------\n")

    """
    Adjusting settings
    """
    # Browsing settings
    options = Options()
    options.add_argument('--headless')
    options.add_argument("--disable-extension")
    options.add_argument('--disable-blink-features=AutomationControlled')

    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)
    driver.get('https://www.compraonline.bonpreuesclat.cat/products')
    ## Properties of objects
    dictionary = dict(id=list(),
                      section_0=list(),
                      section_1=list(),
                      section_2=list(),
                      section_3=list(),
                      name=list(),
                      price=list(),
                      discount=list(),
                      price_x_unit=list(),
                      units=list(),
                      link=list(),
                      datestamp=list())
    return driver, dictionary, write_path


def iterate_sections(driver):
    list_links = []

    def enter_section(driver, avoid=None):
        soup = BeautifulSoup(driver.page_source, "lxml")
        sections = soup.find_all('ul', id='nav-menu')
        sections = sections[-1]
        sections = sections.find_all('li')
        for section in sections[::-1]:
            if re.search('aria-haspopup="true"', str(section)):
                try:
                    WebDriverWait(driver, 5) \
                        .until(EC.element_to_be_clickable((By.XPATH,
                                                           "(//a[@data-test='" + section.text + "'])[last()]"))) \
                        .click()
                    enter_section(driver, section.text)
                except:
                    print(section.text, '     Error!!!!')
            elif section.text != avoid:
                second_link = section.find('a')['href']
                webpage = 'https://www.compraonline.bonpreuesclat.cat' + second_link
                list_links.append(webpage)

    # Click on macro categories
    WebDriverWait(driver, 50) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'button#nav-menu-button'))) \
        .click()
    enter_section(driver)
    driver.quit()
    return set(list_links)


def extract_data(cookies, section_list, dictionary):
    def none_conv(func):
        try:
            return func.text.strip()
        except:
            return None

    def list_index(list_, index):
        try:
            return list_[index]
        except:
            return None

    def loop_sections(sections):
        all_ = [x.text for x in sections]
        section_0, section_1, section_2, section_3 = list_index(all_, 0), list_index(all_, 1), list_index(all_, 2), list_index(all_, 3)
        return section_0, section_1, section_2, section_3

    for link in section_list:
        res = requests.get(link, cookies=cookies)
        soup = BeautifulSoup(res.content, 'lxml')
        sections = soup.find('ul', class_=re.compile('breadcrumb'))
        sections = sections.find_all('li')
        section_0, section_1, section_2, section_3 = loop_sections(sections)
        container = soup.find('div', attrs={'data-synthetics': "product-list"})
        products = container.find_all('div', attrs={'data-test': "fop-body"})
        print(section_1)
        print('     ', section_2)
        print('         ', section_3, '\n')
        for product in products:
            dictionary['id'].append(product.find('a', attrs={'data-test': "fop-product-link"})['href'].replace('/products/', '').replace('/details', ''))
            dictionary['section_0'].append(section_0)
            dictionary['section_1'].append(section_1)
            dictionary['section_2'].append(section_2)
            dictionary['section_3'].append(section_3)
            dictionary['name'].append(none_conv(product.find('a', attrs={'data-test': "fop-product-link"})))
            dictionary['discount'].append(none_conv(product.find('div', attrs={'data-test': "fop-offer"})))
            units = product.find('div', attrs={'data-test': "fop-size"}).text
            dictionary['units'].append(units.replace(re.search("\((.+)\)", units).group(), ''))
            dictionary['price_x_unit'].append(re.search("\((.+)\)", units).group())
            dictionary['price'].append(float(
                product.find('strong', attrs={'data-test': "fop-price"}).text.replace(' €', '').replace(',',
                                                                                                        '.').replace(
                    'valor aproximado', '')))
            dictionary['link'].append('https://www.compraonline.bonpreuesclat.cat' +
                                      product.find('a', attrs={'data-test': "fop-product-link"})['href'])
            dictionary['datestamp'].append(datetime.datetime.now())
        time.sleep(random.randint(0, 1))


def main():
    # time.sleep(30)
    driver, dictionary, write_path = settings()
    # Get the start time for execution duration
    st = time.time()

    # Accept cookies
    WebDriverWait(driver, 50).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'button#onetrust-accept-btn-handler')))
    time.sleep(1)
    WebDriverWait(driver, 50) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'button#onetrust-accept-btn-handler'))) \
        .click()

    # Click on language settings
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button#select-language-menu-button')))
    # driver.save_screenshot("./hurdle.png")
    WebDriverWait(driver, 50) \
        .until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                           'button#select-language-menu-button'))) \
        .click()

    # Choose Spanish
    WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Castellano')]")))
    WebDriverWait(driver, 50) \
        .until(EC.element_to_be_clickable((By.XPATH,
                                           "//*[contains(text(), 'Castellano')]"))) \
        .click()

    # Saving cookies (which means we save the current internal settings of the webpage, like the language)
    driver_cookies = driver.get_cookies()
    driver_cookies = {c['name']: c['value'] for c in driver_cookies}

    """
    Supermarket page
    """
    list_links = iterate_sections(driver)
    extract_data(driver_cookies, list_links, dictionary)

    # get the end time
    et = time.time()

    # get the execution time
    elapsed_time = et - st
    print('Execution time:', elapsed_time, 'seconds')

    df = pd.DataFrame(dictionary)
    df = df.drop_duplicates(subset=['id', 'name', 'price', 'discount', 'price_x_unit', 'units', 'link'])
    df['section_0'] = df['section_0'].astype('category')
    df['section_1'] = df['section_1'].astype('category')
    df['section_2'] = df['section_2'].astype('category')
    df['section_3'] = df['section_3'].astype('category')
    df['discount'] = df['discount'].astype('category')
    df['price'] = df['price'].astype('float')
    df.to_parquet(write_path + 'bonpreuesclat_' + str(datetime.date.today().strftime('%Y-%m-%d')).replace('-', '_') + '.parquet')


if __name__ == "__main__":
    main()
# END

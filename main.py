import json
import time
from selenium import webdriver
from selenium_stealth import stealth
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from functions import collect_product_info


def init_webdriver():
    driver = webdriver.Chrome()
    stealth(driver,
            languages=["en-US", "en"],
            platform="win32")

    driver.get(url='https://ozon.kz/')
    time.sleep(2)

    return driver

def get_products_links(item_name='headphones Xiaomi'):
    driver = init_webdriver()

    find_input = driver.find_element(By.NAME, 'text')
    find_input.clear()

    find_input.send_keys(item_name)
    time.sleep(2)

    find_input.send_keys(Keys.RETURN)
    time.sleep(2)
    current_url = f'{driver.current_url}&sorting=rating'
    driver.get(url=current_url)
    time.sleep(2)

    try:
        find_links = driver.find_elements(By.CLASS_NAME, 'tile-clickable-element')
        products_urls = [f'{link.get_attribute("href")}' for link in find_links]
        print('[+] Product links are collected!')
    except:
        print('[!] Something went wrong!')

    products_urls_dist = {}

    for k,v in enumerate(products_urls):
        products_urls_dist.update({k: v})
    with open('products_urls_dist.json', 'w', encoding='utf-8') as file:
        json.dump(products_urls_dist, file, indent=4, ensure_ascii=False)
    time.sleep(2)

    products_data = []

    for url in products_urls:
        data = collect_product_info(driver=driver, url=url)
        print(f'[+] Products information collected with id: {data.get("product_id")}' )
        time.sleep(2)
        products_data.append(data)


    with open('products_data.json', 'w', encoding='utf-8') as file:
        json.dump(products_data, file, indent=4, ensure_ascii=False)

    unique_products_data = []
    seen_product_ids = set()

    for data in products_data:
        if data["product_id"] not in seen_product_ids:
            unique_products_data.append(data)
            seen_product_ids.add(data["product_id"])

    with open('products_data.json', 'w', encoding='utf-8') as file:
        json.dump(unique_products_data, file, indent=4, ensure_ascii=False)


    return driver


def insert_into_postgres(products_data):
    conn = psycopg2.connect("dbname=ozon_products user=postgres password=1234 host=localhost")
    cur = conn.cursor()

    for item in products_data:
        cur.execute("""
            INSERT INTO products (
                product_id, 
                product_name, 
                product_stars, 
                product_reviews, 
                product_base_price, 
                product_discount_price
            ) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            item.get("product_id"),
            item.get("product_name"),
            item.get("product_stars"),
            item.get("product_reviews"),
            item.get("product_base_price"),
            item.get("product_discount")
        ))

    conn.commit()
    cur.close()
    conn.close()
    print("[+] Data inserted into PostgreSQL!")


if __name__ == '__main__':
    driver = get_products_links()
    driver.close()
    driver.quit()

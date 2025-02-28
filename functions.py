import time as tm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

def collect_product_info(driver, url=''):
    driver.switch_to.new_window('tab')

    tm.sleep(2)
    driver.get(url=url)
    tm.sleep(2)

    product_id_element = driver.find_element(By.XPATH, '//div[contains(text(), "Article code: ")]')

    product_id_text = product_id_element.text

    product_id = product_id_text.split('Article code: ')[1]

    page_source = str(driver.page_source)
    soup = BeautifulSoup(page_source, 'lxml')


    #Тест кода на скачанной странице
    with open(f'product_{product_id}.html', 'w', encoding='utf-8') as file:
        file.write(page_source)

    product_name = soup.find('div', attrs={'data-widget': 'webProductHeading'}).find(
        'h1').text.strip().replace('\t', '').replace('\n', ' ')

    try:
        product_statistics = soup.find(
            'div', attrs={'data-widget': "webSingleProductScore"}).text.strip()
        if "•" in product_statistics:
            product_stars, product_reviews = product_statistics.split(' • ')
            product_stars = product_stars.strip()
            product_reviews = product_reviews.strip()
        else:
            product_stars = product_statistics
            product_reviews = None
    except:
        product_statistics = None
        product_stars = None
        product_reviews = None


    try:
        ozon_price = soup.find('div', attrs={'data-widget': 'webPrice'}).find_all('span')
        if len(ozon_price) == 2:
            product_base_price = ozon_price[1].text.strip().replace("\u2009", " ")
            product_discount_price = ozon_price[0].text.strip().replace("\u2009", " ")
        elif len(ozon_price) == 1:
            product_base_price = ozon_price[1].text.strip().replace("\u2009", " ")
            product_discount_price = None
        else:
            product_base_price = None
            product_discount_price = None

    except AttributeError:
        product_base_price = None
        product_discount_price = None

    product_data = (
        {'product_id' : product_id,
        'product_name' : product_name,
        'product_stars' : product_stars,
        'product_reviews' : product_reviews,
        'product_base_price' : product_base_price,
        'product_discount_price' : product_discount_price
         }
    )
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return product_data

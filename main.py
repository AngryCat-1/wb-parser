import io
import json
import os
import re
import time
from collections import Counter
import selenium
from selenium import webdriver
from colorama import init, Fore
from colorama import Back
from colorama import Style
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from tqdm import tqdm
import requests

print("""
    ██╗    ██╗██████╗       ██████╗  █████╗ ██████╗ ███████╗███████╗██████╗ 
    ██║    ██║██╔══██╗      ██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔════╝██╔══██╗
    ██║ █╗ ██║██████╔╝█████╗██████╔╝███████║██████╔╝███████╗█████╗  ██████╔╝
    ██║███╗██║██╔══██╗╚════╝██╔═══╝ ██╔══██║██╔══██╗╚════██║██╔══╝  ██╔══██╗
    ╚███╔███╔╝██████╔╝      ██║     ██║  ██║██║  ██║███████║███████╗██║  ██║
     ╚══╝╚══╝ ╚═════╝       ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝
    """)
print(Fore.LIGHTBLUE_EX + "by angrycat")
print(Fore.LIGHTBLUE_EX + "discord -> angrycat345")
with open('config.json', 'r') as file:
    config_data = json.load(file)

print(Fore.LIGHTGREEN_EX + "Config loaded successfully")

url = config_data['url']
work_mode = config_data['work_mode (1 is invisible mode, 0 is visible mode)']
load_images = config_data['images_use (1 is True, 0 is False)']
download_images = config_data['images_download (1 is True, 0 is False)']
headless = config_data['selenium_headless (1 is True, 0 is False)']

while True:
    use_number = input(Fore.GREEN + "\n\n1) Parse data (settings in config)\n2) The most popular word in date. (Requires completed data.json)\n3) Clean up 'identical cards'\n-> ")

    def new_url_oneplus(url, added_index):
        base_url, query_string = url.split('?')
        params = query_string.split('&')

        new_params = []
        for param in params:
            key, value = param.split('=')
            if key == 'page':
                value = str(int(value) + added_index)
            new_params.append(f"{key}={value}")

        return f"{base_url}?{'&'.join(new_params)}"


    def download_image_by_url(img_url, img_name):
        img_data = requests.get(img_url).content
        with open(f'images/{img_name}.webp', 'wb') as handler:
            handler.write(img_data)

    if use_number == "1":
        parsed_data = {}
        pages_url = []
        cards_url = []

        options = Options()
        if work_mode == 1:
            if headless == 1:
                options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)
        driver.get(url)
        print(Fore.LIGHTGREEN_EX + "\n\nSelenium loaded successfully")
        time.sleep(1)

        url_index_page = 0
        FoundedResult = False
        EndCycle = False
        print(Fore.LIGHTBLUE_EX + "WB Pages have started loading")
        while FoundedResult == False:
            if EndCycle:
                FoundedResult = True
                continue
            time.sleep(0.2)
            try:
                productcard = driver.find_element(By.CLASS_NAME, 'product-card__wrapper')
                url_index_page += 1
                new_url = new_url_oneplus(url, url_index_page)
                driver.get(new_url)
                time.sleep(0.2)
                print(f"Loaded -> {url_index_page} <- page")
                pages_url.append(new_url)
            except:
                EndCycle = True


        print(Fore.LIGHTGREEN_EX + f"WB Pages loaded successfully ({len(pages_url)})")
        print(Fore.LIGHTBLUE_EX + "WB Cards URL have started loading")

        for page_url in tqdm(pages_url):
            driver.get(page_url)
            time.sleep(0.2)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(0.08)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(0.08)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(0.08)
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
            time.sleep(0.08)

            product_card_list = driver.find_element(By.CLASS_NAME, 'product-card-list')
            product_cards = product_card_list.find_elements(By.CLASS_NAME, 'product-card')

            for card in product_cards:
                cards_url.append(card.find_element(By.CLASS_NAME, 'product-card__link').get_attribute('href'))

        print(Fore.LIGHTGREEN_EX + f"WB Cards URL loaded successfully ({len(cards_url)})")


        cards = []
        print(Fore.LIGHTBLUE_EX + "WB Cards have started loading")

        for card_url in tqdm(cards_url):
            try:
                driver.get(card_url)
                time.sleep(1)

                card_info = {}

                card_info['title'] = driver.find_element(By.CLASS_NAME, 'product-page__header').find_element(By.CLASS_NAME, 'product-page__title').text
                card_info['rating'] = driver.find_element(By.CLASS_NAME, 'product-review__rating').text
                card_info['rating_count'] = driver.find_element(By.CLASS_NAME, 'product-review__count-review').text
                try:
                    card_info['price_default'] = driver.find_element(By.CLASS_NAME, 'price-block__old-price').text
                except:
                     card_info['price_default'] = "-"

                try:
                    card_info['price_discount'] = driver.find_element(By.CLASS_NAME, 'price-block__final-price').text
                except:
                    card_info['price_discount'] = "-"

                try:
                    card_info['price_wb_wallet'] = driver.find_element(By.CLASS_NAME, 'price-block__wallet-price').text
                except:
                     card_info['price_wb_wallet'] = "-"


                try:
                    card_info['brand'] = driver.find_element(By.CLASS_NAME, 'product-page__header-brand').text
                except:
                    card_info['brand'] = "-"

                card_info['sold_params'] = {}

                hover = driver.find_element(By.CLASS_NAME, "product-page__seller-wrap ").find_element(By.CLASS_NAME, 'seller-info__more')
                actions = ActionChains(driver)
                actions.move_to_element(hover).perform()
                elements_seller_info_block = driver.find_element(By.CLASS_NAME, 'tooltip-seller-info')
                elements_seller_infos = elements_seller_info_block.find_elements(By.CLASS_NAME, 'seller-params__item')
                for element in elements_seller_infos:
                   element_name = element.find_element(By.CLASS_NAME, 'seller-params__desc').text
                   element_value = element.find_element(By.CLASS_NAME, 'seller-params__value').text
                   card_info['sold_params'][element_name] = element_value
                print()


                param_block_container = driver.find_element(By.CLASS_NAME, 'product-params__table')
                params_blocks = param_block_container.find_elements(By.CLASS_NAME, "product-params__row")

                card_info['params'] = {}
                wb_id_card = -1


                for param in params_blocks:
                    param_name = param.find_element(By.CLASS_NAME, "product-params__cell-decor").text
                    param_value = param.find_elements(By.CLASS_NAME, "product-params__cell")[1].text
                    if wb_id_card == -1:
                        wb_id_card = param_value
                    card_info['params'][param_name] = param_value


                if load_images == 1:
                    try:
                        card_info['img'] = driver.find_element(By.CLASS_NAME, "product-page__main-slider").find_element(By.CLASS_NAME, "slide__content").find_element(By.TAG_NAME, "img").get_attribute("src")
                    except Exception:
                        pass

                    try:
                        card_info['img'] = driver.find_element(By.CLASS_NAME, "product-page__main-slider").find_element(By.CLASS_NAME, "slide__content").find_element(By.TAG_NAME, "video").get_attribute("src")
                    except Exception:
                        pass

                    if download_images == 1:
                        download_image_by_url(card_info['img'], wb_id_card)

                cards.append(card_info)

                with io.open('data.json', 'w', encoding="utf-8") as json_file:
                    json.dump(cards, json_file, ensure_ascii=False)
            except Exception as EE:
                print(EE)
                pass


    elif use_number == "2":
        with io.open('data.json', "r", encoding="utf-8") as f:
            data_json = json.load(f)

        all_titles = " ".join(item['title'] for item in tqdm(data_json))
        all_titles_cleaned = re.sub(r'[^\w\s]', '', all_titles).lower()
        words = all_titles_cleaned.split()
        word_counts = Counter(words)

        most_common_word, frequency = word_counts.most_common(1)[0]

        print(Fore.LIGHTGREEN_EX + f"The most popular word is the'{most_common_word}' that appeared {frequency} times.")

    elif use_number == "3":
        with io.open('data.json', "r", encoding="utf-8") as f:
            data_json = json.load(f)

        print(Fore.BLUE + f"The clear has begun. Wait")
        names_pool = []
        new_cards = []
        normal_cards = 0
        deleted_cards = 0
        for card in tqdm(data_json):
            if card['title'] in names_pool:
                deleted_cards += 1
            else:
                new_cards.append(card)
                names_pool.append(card['title'])
                normal_cards += 1

        print(Fore.LIGHTGREEN_EX + f"Checked {normal_cards} cards")
        print(Fore.RED + f"Deleted {deleted_cards} cards")


        with io.open('data.json', 'w', encoding="utf-8") as json_file:
            json.dump(new_cards, json_file, ensure_ascii=False)



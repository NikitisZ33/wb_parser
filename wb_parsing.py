import csv
import time
from aiogram.types import FSInputFile
import requests
import logging
import asyncio
import config
from aiogram import Bot, types
from aiogram.enums import ParseMode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import random

API_KEY = config.API_KEY
bot = Bot(API_KEY)
logging.basicConfig(level=logging.ERROR)

chat_id = '-1002094001727'

headers = {
    'authority': 'www.wildberries.by',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    # 'cookie': '_wbauid=5655241211706555466',
    'if-modified-since': 'Thu, 01 Feb 2024 16:44:47 GMT',
    'if-none-match': '"65bbca7f-f6c"',
    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}


width = 900
height = 1100

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument(f'--window-size={width},{height}')


async def start():
    while True:
        with open('urls_by.csv', 'r') as f:
            read = list(csv.reader(f, delimiter=';'))
            try:
                if len(read):
                    random_row = random.choice(read[1:])
                    ids, _, _, nodes = random_row
                    try:
                        response = requests.get(
                            f'https://catalog.wb.ru/catalog/{nodes}/v1/catalog?cat={ids}&limit=100&sort=popular&'
                            f'page={1}&appType=128&curr=byn&lang=ru&dest=-59208&spp=30&&discount=70&'
                            f'TestGroup=no_test&TestID=no_test', headers=headers).json()

                        for product in response['data']['products']:
                            i = product['id']
                            name = product['name']
                            salePriceU = str(product['salePriceU'])
                            salePrice = f"{salePriceU[:-2]}.{salePriceU[-2:]}"
                            sale = product['sale']
                            brand = product['brand']
                            if int(salePriceU[:-2]) <= 70:
                                result_message = (f"<u>Название</u>:  <b>{name}</b>\n"
                                                  f"<u>Цена</u>:  <b>{salePrice}</b>\n"
                                                  f"<u>Скидка</u>:  <b>{sale}%</b>\n"
                                                  f"<u>Бренд</u>:  <b>{brand}</b>\n"
                                                  f'<u>Ссылка</u>:  <a href="https://www.wildberries.by/product?card={i}&category={ids}">{name}</a>')
                                await selenium_image(f'https://www.wildberries.by/product?card={i}&category={ids}">{name}')
                                await tg_chanal(result_message)
                            else:
                                continue
                            await asyncio.sleep(0)
                    except requests.RequestException as e:
                        logging.error(f"An error occurred: {e}")
                        continue
            except: continue


async def tg_chanal(result_message):
    photo_path = 'D:\wb_parser\screenshot.png'  # Replace with the actual path to your photo
    photo = FSInputFile(photo_path)
    await bot.send_photo(chat_id=chat_id, photo=photo, caption=result_message, parse_mode=ParseMode.HTML)


async def selenium_image(link):
    driver = webdriver.Chrome(options=chrome_options)
    url = link
    driver.get(url)
    time.sleep(10)
    screenshot_path = 'screenshot.png'
    driver.save_screenshot(screenshot_path)

    # Закрываем браузер
    driver.quit()
    return

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()



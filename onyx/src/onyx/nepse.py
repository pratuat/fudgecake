import pdb

import requests, re
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
# from threading import Thread
# from concurrent.futures import ThreadPoolExecutor
# from src.utils.request_manager import RequestManager
import src.utils.logger_utils as logger_utils

logger = logger_utils.get_logger(filename='onyx.log', name=__name__, level='DEBUG')

class MongoStore:
    client = MongoClient(host="localhost", port=27017, username='root', password='password')

    @classmethod
    def upload_transaction(cls, transactions):
        db = cls.client.get_database('onyx')
        collection = db.get_collection('transactions')

        updates = [UpdateOne({"_id" : transaction.get("contract_no")}, {"$set" : {**transaction}}, upsert=True) for transaction in transactions]
        collection.bulk_write(updates)

class NEPSE:
    floorsheet_url = "http://www.nepalstock.com/main/floorsheet/index/{page}"

    @classmethod
    def download_floorsheet(cls, callback=None):
        page_count = cls.fetch_page(page=1, callback=callback)

        for page in range(2, page_count+1):
            cls.fetch_page(page=page, callback=callback)

        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     for page in range(2, page_count+1):
        #         executor.submit(cls.fetch_page, kwargs={'page' : page, 'callback' : callback})

        # for page in range(2, page_count+1):
        #     thread = Thread(target=cls.fetch_page, kwargs={'page' : page, 'callback' : callback})
        #     RequestManager.request(thread.start, log_info=f"Page:{page}")

        return "ok"

    @classmethod
    def fetch_page(cls, page, callback):
        try:
            response = requests.get(cls.floorsheet_url.format(page=page), params=cls.get_params(page))
            transactions = cls.scrape_transactions(response.text)
            logger.debug(f"\tPage:{page}\tStatus:{response.status_code}\tTransactionCount:{len(transactions)}")

            if callback:
                callback(transactions)

            if page == 1:
                return cls.get_page_count(response.text)
            else:
                return None
        except Exception as e:
            logger.error(f"Error scraping page {page}.")

        return None

    @classmethod
    def get_page_count(cls, text):
        soup = BeautifulSoup(text, features="lxml")
        rows = soup.find(id='home-contents').find_all('tr')
        page_count = int(re.search(r'Page 1/[0-9]*', str(rows[-3])).group().split('/')[1])

        return page_count

    @classmethod
    def scrape_transactions(cls, text):
        soup = BeautifulSoup(text, features="lxml")
        rows = soup.find(id='home-contents').find_all('tr')

        transactions = []

        for row in rows[2:-3]:
            values = row.get_text().strip().split('\n')[1:]
            transactions.append({
                'contract_no' : int(values[0]),
                'stock_symbol' : values[1],
                'buyer_broker' : values[2],
                'seller_broker': values[3],
                'quantity' : int(values[4]),
                'rate' : float(values[5]),
                'amount' : float(values[6]),
            })

        return transactions

    def get_params(cls):
        return (
            ('_limit', '500'),
        )

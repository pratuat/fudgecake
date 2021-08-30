import requests, re, datetime, os
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
import src.utils.logger_utils as logger_utils

# from threading import Thread
# from concurrent.futures import ThreadPoolExecutor
# from src.utils.request_manager import RequestManager

logger = logger_utils.get_logger(filename='onyx.log', name=__name__, level='DEBUG')

class MongoStore:
    client = MongoClient(
        host=os.getenv('MONGODB_HOST'),
        port=int(os.getenv('MONGODB_PORT')),
        username=os.getenv('MONGODB_USER'),
        password=os.getenv('MONGODB_PASSWORD'),
    )

    db = client.get_database(os.getenv('MONGODB_DATABASE'))

    @classmethod
    def upload_transaction(cls, transactions):
        collection = cls.db.get_collection('transactions')
        updates = [UpdateOne({"_id" : transaction.get("contract_no")}, {"$set" : {**transaction}}, upsert=True) for transaction in transactions]
        collection.bulk_write(updates)
class NEPSE:
    floorsheet_url = "http://www.nepalstock.com/main/floorsheet/index/{page}"

    @classmethod
    def download_floorsheet(cls, callback=None):
        print("NEPSE.download_floorsheet ...")
        page_count, date = cls.get_day_infos()

        print(f"Page count:{page_count} Date: {date}")

        for page in range(1, page_count+1):
            cls.fetch_page(page=page, date=date, callback=callback)

        # with ThreadPoolExecutor(max_workers=10) as executor:
        #     for page in range(2, page_count+1):
        #         executor.submit(cls.fetch_page, kwargs={'page' : page, 'callback' : callback})

        # for page in range(2, page_count+1):
        #     thread = Thread(target=cls.fetch_page, kwargs={'page' : page, 'callback' : callback})
        #     RequestManager.request(thread.start, log_info=f"Page:{page}")

        return "ok"

    @classmethod
    def fetch_page(cls, page, date, callback):
        print("Fetching page ", page)
        try:
            response = requests.get(cls.floorsheet_url.format(page=page), params=cls.get_params())
            transactions = cls.scrape_transactions(date, response.text)
            logger.debug(f"\tPage:{page}\tStatus:{response.status_code}\tTransactionCount:{len(transactions)}")

            if callback:
                callback(transactions)

            return None
        except Exception as e:
            print("Error ...")
            logger.error(f"Error scraping page {page}.")

        return None

    @classmethod
    def get_day_infos(cls):
        response = requests.get(cls.floorsheet_url.format(page=1), params=cls.get_params())
        soup = BeautifulSoup(response.text, features="lxml")
        rows = soup.find(id='home-contents').find_all('tr')
        page_count = int(re.search(r'Page 1/[0-9]*', str(rows[-3])).group().split('/')[1])

        date_node = soup.find(id='ticker').find(id='date')
        date = re.search(r'20[0-9][0-9]-[0-1][1-9]-[0-3][0-9]', date_node.get_text()).group()
        date = datetime.datetime.strptime(date, "%Y-%m-%d")

        return [page_count, date]

    @classmethod
    def scrape_transactions(cls, date, text):
        soup = BeautifulSoup(text, features="lxml")
        rows = soup.find(id='home-contents').find_all('tr')

        transactions = []

        for row in rows[2:-3]:
            values = row.get_text().strip().split('\n')[1:]
            transactions.append({
                'date' : date,
                'contract_no' : int(values[0]),
                'stock_symbol' : values[1],
                'buyer_broker' : values[2],
                'seller_broker': values[3],
                'quantity' : int(values[4]),
                'rate' : float(values[5]),
                'amount' : float(values[6]),
            })

        return transactions

    @classmethod
    def get_params(cls):
        return (
            ('_limit', '500'),
        )

if __name__ == '__main__':

    import sys
    print(sys.path)
    print("=" * 50)
    print("Calling scraping job...")
    callback = MongoStore.upload_transaction
    NEPSE.download_floorsheet(callback=callback)

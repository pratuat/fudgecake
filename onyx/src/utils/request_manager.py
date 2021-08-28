import time
import threading
import src.utils.logger_utils as logger_utils
from src.utils.dict_utils import deep_get

class RequestManager:
    logger = logger_utils.get_logger(name=__name__, level='DEBUG')

    # Lock instance to enforce request stoppage after REQUEST_THRESHOLD number of requests
    # obtain lock before modifying counter
    counter = 0
    counter_lock = threading.Lock()

    # negligible value for now
    SLEEP_TIME_1= 0
    SLEEP_TIME_2= 0
    REQUEST_THRESHOLD = 20

    # Lock/Semphore to control throttle of outgoing request
    # throttle_lock = threading.Lock()
    throttle_semaphore = threading.Semaphore(value=10)

    last_request = time.time()

    @classmethod
    def limit_api_call(cls):
        with cls.counter_lock:
            if cls.counter > cls.REQUEST_THRESHOLD:
                cls.logger.debug(f"REQUEST LIMIT. Sleeping for {cls.SLEEP_TIME_1} seconds.")
                time.sleep(cls.SLEEP_TIME_1)
                cls.counter = 0
            else:
                cls.counter += 1

    @classmethod
    def request(cls, target, *pargs, log_info=None, **kargs):
        try:
            cls.limit_api_call()
            with cls.throttle_semaphore:
                time.sleep(cls.SLEEP_TIME_2)

                current_request = time.time()
                target(*pargs, **kargs)

                cls.logger.debug(f"{log_info}\t{current_request-cls.last_request:0.2f}")
                cls.last_request = current_request

                return None
        except Exception as e:
            cls.logger.error(f"\t{type(e).__name__}\t{log_info}\t{e.args}")

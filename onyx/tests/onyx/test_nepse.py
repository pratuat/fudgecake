import unittest
from src.onyx.nepse import NEPSE, MongoStore

class TestNEPSE(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_download_floorsheet(self):
        callback = MongoStore.upload_transaction
        ret_value = NEPSE.download_floorsheet(callback=callback)

        self.assertEqual(ret_value, "ok")

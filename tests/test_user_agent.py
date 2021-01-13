from unittest import TestCase

from config import *
from intel_platform.src.agents.user import UserAgent
from utils.data_store.rds_data_store import RDSDataStore

rds_data_store = RDSDataStore(host=PG_HOST,
                              port=PG_PORT,
                              dbname=PG_DBNAME,
                              user=PG_USER,
                              password=PG_PASSWORD)


class TestClientAgent(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestClientAgent, self).__init__(*args, **kwargs)

    def setUp(self):
        self.rds_data_store = rds_data_store
        with open("init.sql", "r") as fp:
            self.rds_data_store.run_create_table_sql(fp.read())

    def tearDown(self):
        with open("init.sql", "r") as fp:
            self.rds_data_store.run_create_table_sql(fp.read())

    def _add_user(self):
        csv_file_name = "tests/data/user.csv"
        cursor = self.rds_data_store.conn.cursor()
        sql = "COPY users FROM STDIN DELIMITER ',' CSV HEADER"
        with open(csv_file_name, "r") as fp:
            cursor.copy_expert(sql, fp)
        self.rds_data_store.conn.commit()
        cursor.close()

    def test_add_new_user(self):
        status = UserAgent.add_new_user(data_store=rds_data_store, user_id="test_user_id",
                                        full_name="test_full_name",
                                        company_name="test_company_name", hashed_password="test_hashed_password",
                                        disabled=False)
        expected_status = True
        self.assertEqual(first=status, second=expected_status)
        result = self.rds_data_store.run_custom_sql("select * from users")
        result = list(result[0])
        expected_result = ['test_user_id', 'test_full_name', 'test_company_name', 'test_hashed_password', False]
        self.assertListEqual(list1=expected_result, list2=result)

    def test_get_user_details_for_user_id(self):
        self._add_user()

        result = UserAgent.get_user_details_for_user_id(data_store=self.rds_data_store,
                                                        user_id="test_user_id")
        expected_result = {'user_id': 'test_user_id', 'full_name': 'test_full_name',
                           'company_name': 'test_company_name', 'hashed_password': 'test_hashed_password',
                           'disabled': False}
        self.assertDictEqual(d1=result, d2=expected_result)

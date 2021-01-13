from unittest import TestCase


from config import *
from utils.data_store.rds_data_store import RDSDataStore, IteratorFile

rds_data_store = RDSDataStore(host=PG_HOST,
                              port=PG_PORT,
                              dbname=PG_DBNAME,
                              user=PG_USER,
                              password=PG_PASSWORD)


class TestRDSDataStore(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestRDSDataStore, self).__init__(*args, **kwargs)

    def setUp(self):
        self.rds_data_store = rds_data_store
        self.rds_data_store.run_create_table_sql("drop schema public cascade")
        self.rds_data_store.run_create_table_sql("create schema public")

    def tearDown(self):
        self.rds_data_store.run_create_table_sql("drop schema public cascade")
        self.rds_data_store.run_create_table_sql("create schema public")

    def test_run_create_table_sql(self):
        status = self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id int, value varchar(256))")
        expected_status = True
        self.assertEqual(status, status)

    def test_run_select_sql(self):
        self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id int, value varchar(256))")
        self.rds_data_store.run_insert_into_sql("INSERT INTO hello values(1, 'hello'), (2, 'ciao')")
        result = self.rds_data_store.run_select_sql('SELECT * FROM hello ORDER BY id')
        expected_result = [(1, 'hello'), (2, 'ciao')]
        self.assertCountEqual(first=result, second=expected_result)

    def test_run_insert_into_sql(self):
        self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id int, value varchar(256))")
        result = self.rds_data_store.run_insert_into_sql("INSERT INTO hello values(1, 'hello'), (2, 'ciao')")
        expected_result = True
        self.assertEqual(first=result, second=expected_result)

    def test_run_update_sql(self):
        self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id int, value varchar(256))")
        self.rds_data_store.run_insert_into_sql("INSERT INTO hello values(1, 'hello'), (2, 'ciao')")
        result = self.rds_data_store.run_update_sql("UPDATE hello SET value='yoo' where id=2")
        expected_result = True
        self.assertEqual(first=result, second=expected_result)
        result = self.rds_data_store.run_select_sql('SELECT * FROM hello ORDER BY id')
        expected_result = [(1, 'hello'), (2, 'yoo')]
        self.assertCountEqual(first=result, second=expected_result)

    def test_run_custom_sql(self):
        self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id int, value varchar(256))")
        self.rds_data_store.run_create_table_sql("CREATE TABLE hi(id int, value varchar(256))")
        self.rds_data_store.run_insert_into_sql("INSERT INTO hello values(1, 'hello'), (2, 'ciao')")
        self.rds_data_store.run_insert_into_sql("INSERT INTO hi values(1, 'bye'), (2, 'jao')")
        result = self.rds_data_store.run_custom_sql("select * from hello union select * from hi")
        expected_result = [(2, 'ciao'), (1, 'bye'), (2, 'jao'), (1, 'hello')]
        self.assertCountEqual(first=result, second=expected_result)

    def test_run_batch_delete_sql(self):
        self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id varchar(4), value bigint)")
        self.rds_data_store.run_insert_into_sql(
            "INSERT INTO hello values('1', 23), ('2', 24),('2', 25),('3', 25)")
        query = """delete from {table} where id = '{id}' and value in ({s})""".format(
            table="hello",
            id='2',
            s="%s,%s")
        self.rds_data_store.run_batch_delete_sql(query=query, data_list=[24, 25])
        result = self.rds_data_store.run_custom_sql("select * from hello")
        expected_result = [('1', 23), ('3', 25)]
        self.assertCountEqual(first=result, second=expected_result)

    def test_run_batch_insert_sql(self):
        self.rds_data_store.run_create_table_sql("CREATE TABLE hello(id varchar(4), value bigint)")
        data_list = [["1", 2], ["2", 3], ["2", 4], ["2", 5], ["6", 7]]
        s = "\t".join(["{}" for i in range(2)])
        file = IteratorFile((s.format(data[0], data[1])
                             for data in data_list))
        self.rds_data_store.run_batch_insert_sql(file=file, table="hello", columns=["id", "value"])
        result = self.rds_data_store.run_custom_sql("select * from hello")
        expected_result = [('1', 2), ('2', 3), ('2', 4), ('2', 5), ('6', 7)]
        self.assertCountEqual(first=result, second=expected_result)
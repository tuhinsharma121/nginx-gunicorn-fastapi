import io
import sys

import psycopg2


class RDSDataStore(object):
    def __init__(self, host, port, dbname, user, password):
        self.host = host
        self.port = port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.conn = psycopg2.connect(host=self.host,
                                     port=self.port,
                                     dbname=self.dbname,
                                     user=self.user,
                                     password=self.password)

    def _run_sql_to_get_data(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            mobile_records = cursor.fetchall()
            cursor.close()
            return mobile_records
        except Exception:
            self.conn.rollback()
            return None

    def _run_sql_to_push_data(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            self.conn.commit()
            cursor.close()
            return True
        except Exception as e:
            print(e)
            self.conn.rollback()
            return None

    def run_select_sql(self, query):
        mobile_records = self._run_sql_to_get_data(query=query)
        return mobile_records

    def run_insert_into_sql(self, query):
        return self._run_sql_to_push_data(query=query)

    def run_update_sql(self, query):
        return self._run_sql_to_push_data(query=query)

    def run_custom_sql(self, query):
        mobile_records = self._run_sql_to_get_data(query=query)
        return mobile_records

    def run_create_table_sql(self, query):
        return self._run_sql_to_push_data(query=query)

    def run_batch_insert_sql(self, file, table, columns):
        try:
            cursor = self.conn.cursor()
            cursor.copy_from(file=file, table=table, columns=columns)
            self.conn.commit()
            cursor.close()
            return True
        except Exception:
            self.conn.rollback()
            return None

    def run_batch_delete_sql(self, query, data_list):
        try:
            cursor = self.conn.cursor()
            sql = cursor.mogrify(query, data_list)
            cursor.execute(sql)
            self.conn.commit()
            return True
        except Exception:
            self.conn.rollback()
            return None


class IteratorFile(io.TextIOBase):
    """ given an iterator which yields strings,
    return a file like object for reading those strings """

    def __init__(self, it):
        self._it = it
        self._f = io.StringIO()

    def read(self, length=sys.maxsize):

        try:
            while self._f.tell() < length:
                self._f.write(next(self._it) + "\n")

        except StopIteration as e:
            pass

        finally:
            self._f.seek(0)
            data = self._f.read(length)
            remainder = self._f.read()
            self._f.seek(0)
            self._f.truncate(0)
            self._f.write(remainder)
            return data
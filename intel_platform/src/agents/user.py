from config import *
import pandas as pd


class UserAgent(object):

    def __init__(self):
        pass

    @classmethod
    def add_new_user(cls, data_store, user_id, full_name, company_name, hashed_password, disabled):
        table = TABLE_USERS
        columns_value_dict = {"user_id": user_id, "full_name": full_name, "company_name": company_name,
                              "hashed_password": hashed_password, "disabled": disabled}

        columns = list(columns_value_dict.keys())
        column = ",".join(columns)
        values = [columns_value_dict[key] for key in columns]
        value = str(tuple(values))

        sql = """INSERT INTO {table} ({column}) VALUES {value}""".format(table=table, column=column, value=value)
        status = data_store.run_insert_into_sql(query=sql)
        return status

    @classmethod
    def get_user_details_for_user_id(cls, data_store, user_id):
        table = TABLE_USERS
        columns = ["user_id", "full_name", "company_name", "hashed_password", "disabled"]
        where = "user_id='{user_id}'".format(user_id=user_id)

        column = ",".join(columns)
        sql = """ SELECT {column} from {table} where {where}""".format(column=column, table=table, where=where)
        mobile_records = data_store.run_select_sql(query=sql)
        df = None
        if mobile_records is not None and len(mobile_records) > 0:
            df = pd.DataFrame.from_records(mobile_records)
            df.columns = columns
        client_details = None
        if df is not None:
            client_details = df[columns].to_dict(orient="records")[0]
        return client_details


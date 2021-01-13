import datetime
from unittest import TestCase
from unittest.mock import Mock, patch

import pytz
from fastapi.testclient import TestClient

from intel_platform.deployment.server import app, logger

logger.disabled = True

client = TestClient(app)
datetime_mock = Mock(wraps=datetime.datetime)
tz = pytz.timezone("Asia/Kolkata")
datetime_now = tz.localize(datetime.datetime(2020, 5, 30, 13, 0, 0, 0))
datetime_mock.now.return_value = datetime_now


class TestServer(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestServer, self).__init__(*args, **kwargs)

    def setUp(self):
        with open("init.sql", "r") as fp:
            app.rds_data_store.run_create_table_sql(fp.read())

    def tearDown(self):
        with open("init.sql", "r") as fp:
            app.rds_data_store.run_create_table_sql(fp.read())

    def test_home_page(self):
        response = client.get("/")
        status_code = response.status_code
        expected_status_code = 200
        self.assertEqual(first=status_code, second=expected_status_code)
        response_json = response.json()
        expected_response_json = {'message': 'Apis for nginx-gunicorn-fastapi', 'status': 200}
        self.assertDictEqual(d1=response_json, d2=expected_response_json)

    def test_sign_up_new_client(self):
        response = client.post(
            "/api/v1/schemas/user/sign-up",
            headers={"accept": "application/json"},
            json={"user_id": "test_user", "company_name": "test_company_name", "full_name": "test_full_name",
                  "disabled": False, "password": "test_password"}
        )
        status_code = response.status_code
        expected_status_code = 200
        self.assertEqual(first=status_code, second=expected_status_code)
        response_json = response.json()
        expected_response_json = {"status": "200",
                                  "message": "Sign up for new user with user_id test_user is successful."}
        self.assertDictEqual(d1=response_json, d2=expected_response_json)

        response = client.post(
            "/api/v1/schemas/user/sign-up",
            headers={"accept": "application/json"},
            json={"user_id": "test_user", "company_name": "test_company_name", "full_name": "test_full_name",
                  "disabled": False, "password": "test_password"}
        )
        status_code = response.status_code
        expected_status_code = 200
        self.assertEqual(first=status_code, second=expected_status_code)
        response_json = response.json()
        expected_response_json = {"status": "409", "message": "User_id test_user is already registered."}
        self.assertDictEqual(d1=response_json, d2=expected_response_json)

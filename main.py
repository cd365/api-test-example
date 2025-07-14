import logging
import pytest
import requests
from diskcache import Cache as DiskCache
from google_authenticator import generate_totp
from typing import Any, Dict, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# Defining constants
BASE_URL = "http://192.168.1.8:8899/example/v1"
USERNAME = "username"
PASSWORD = "password"
GOOGLE_AUTH_SECRET = "U5WM5NKSC757E5A6" # Google auth secret
CONTENT_TYPE = "Content-Type"
CONTENT_TYPE_VALUE = "application/json"
AUTHORIZATION = "Authorization"


# File Cache
file_cache = DiskCache(".cache") # Specify the cache directory

# 日志
logging.basicConfig(
	level=logging.INFO, # Setting the log level
	format='%(asctime)s - %(levelname)s - %(message)s', # Log Format
)
logger = logging.getLogger(__name__)

logger.info("script started")

# Append query parameter key-value pairs to the URL.
def url_query_params(url :str, params: Optional[Dict] = None) -> str:
	if not url.startswith(BASE_URL):
		url = f"{BASE_URL}{url}"
	if params is None:
		return url
	parsed_url = urlparse(url)
	query_params = parse_qs(parsed_url.query)
	result :Dict[str:str] = {}
	for key, value in query_params.items():
		if value is not None:
			result[key] = ",".join(value)
	for key, value in params.items():
		if value is not None:
			result[key] = str(value)
	new_query = urlencode(result, doseq=True)
	new_url = urlunparse((
		parsed_url.scheme,
		parsed_url.netloc,
		parsed_url.path,
		parsed_url.params,
		new_query,
		parsed_url.fragment
	))
	return new_url

class TestPublicApi:
	"""Testing interfaces that do not require authentication"""

	def setup_method(self):
		"""Initialize request header"""
		self.headers = {CONTENT_TYPE: CONTENT_TYPE_VALUE}

	def test_get_example1(self):
		print(self.headers)

	def test_put_example2(self):
		print(self.headers)

	def test_post_example3(self):
		print(self.headers)

	def test_delete_example4(self):
		print(self.headers)

class TestPrivateApi:
	"""Testing interfaces that require authentication"""

	limit_offset: Dict[str, None|float|int|str] = {"limit": 20, "offset": 0}

	def setup_method(self):
		"""Initialization: Get Token and set request header"""

		self.headers = {CONTENT_TYPE: CONTENT_TYPE_VALUE}
		self.user_data = {}

		cache_key = "my_test_token"
		cache_value = file_cache.get(cache_key)
		if cache_value is not None:
			token = str(cache_value)
			self.headers[AUTHORIZATION] = token
			logger.info(f"cache token: {token}")
		else:
			# Login to get a token
			login_data = {
				"username": USERNAME,
				"password": PASSWORD,
				"google_verify_code": generate_totp(GOOGLE_AUTH_SECRET),
			}
			response = requests.post(url_query_params("/login"), json=login_data, headers=self.headers)
			assert response.status_code == 200, f"Login failed: {response.text}"
			data = response.json()
			token = data['data']['token']
			self.headers[AUTHORIZATION] = token
			file_cache.set(cache_key, token, expire=1800) # cache 30 minutes
			logger.info(f"login token: {token}")

	def test_get_profile(self):
		"""Get the current user's personal information"""
		response = requests.get(url_query_params("/profile"), headers=self.headers)
		assert response.status_code == 200, f"Failed to obtain the current user's personal information:{response.text}"
		# logger.info(response.text)
		# logger.info(response.json()['data'])

	def test_get_order_list(self):
		query = self.limit_offset.copy()
		query.update({
			"page": 1,
			"limit": 100,
			"keyword": "test",
		})
		response = requests.get(url_query_params("/order/list", query), headers=self.headers)
		assert response.status_code == 200, f"Order list query failed:{response.text}"

	def test_put_example(self):
		query_params: Dict[str, Any] = {"key1": "value1", "key2": ["value2", "value3"]}
		headers: Dict[str, str] = {"Authorization": "Bearer token123", "Content-Type": "application/json"}
		body_form: Dict[str, Any] = {"field1": "value1", "field2": "value2"}
		requests.put(
			url_query_params("/example"),
			params=query_params,
			data=body_form, # body data
    		headers=headers,
		)

	def test_delete_example(self):
		headers: Dict[str, str] = {"Authorization": "Bearer token123", "Content-Type": "application/json"}
		body_json: Dict[str, Any] = {"reason": "Obsolete resource"}
		requests.delete(
			url_query_params("/example"),
			json=body_json,  # body data
			headers=headers,
		)

if __name__ == "__main__":
	pytest.main(["-v", "--html=report.html"])

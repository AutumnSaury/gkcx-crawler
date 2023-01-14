import requests
from requests.adapters import HTTPAdapter, Retry

Retry.DEFAULT_BACKOFF_MAX = 20

session = requests.Session()
retries = Retry(total=10, backoff_factor=1, status_forcelist=[500, 502])
session.mount('https://', HTTPAdapter(max_retries=retries))

session.headers.update({
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json;charset=UTF-8',
    'user-agent': 'Mozilla/5.0'
})

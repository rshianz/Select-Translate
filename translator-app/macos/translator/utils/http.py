import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_UA = "TranslatorApp/1.0 (personal dictionary & translation tool)"


def _session(trust_env: bool, retries=None):
    s = requests.Session()
    s.trust_env = trust_env
    s.headers["User-Agent"] = _UA
    adapter = HTTPAdapter(max_retries=retries) if retries else HTTPAdapter()
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


session = _session(True, Retry(total=2, backoff_factor=0.5,
                               status_forcelist=(429, 500, 502, 503)))

dictionary_session = _session(True)    # via proxy env vars
direct_session = _session(False)       # ignores proxies
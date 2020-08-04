# -*- coding: utf-8 -*-
# pylint: disable=expression-not-assigned,line-too-long
"""Walk the REST accessible path tree of some binary repository management system."""
import datetime as dti
import time
import warnings

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

TS_FORMAT = "%Y-%m-%d %H:%M:%S"


class TreeWalker:  # pylint: disable=bad-continuation,expression-not-assigned
    """Wrap the auth stuff and the REST BRM tree related walking."""

    def __init__(self, server_url, api_root=None, username=None, api_token=None, wait=None):
        self._user_url = server_url.rstrip("/")
        self._base_url = f"{self._user_url}{api_root if api_root else '/'}"
        self._wait = wait if wait else 0.0

        if username and api_token:
            self._session = requests.Session()
            self._session.auth = (username, api_token)
            return
        raise ValueError("Must use API token (other authentication means not implemented)")

    def _fetch(self, url, params=None):
        """DRY."""
        params = {} if not params else params
        self._wait and time.sleep(self._wait)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
            return self._session.get(url, verify=False, params=params)


def naive_timestamp(timestamp=None):
    """Logging helper."""
    if timestamp:
        return timestamp.strftime(TS_FORMAT)
    return dti.datetime.now().strftime(TS_FORMAT)

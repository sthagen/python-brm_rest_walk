# -*- coding: utf-8 -*-
# pylint: disable=expression-not-assigned,line-too-long
"""Walk the REST accessible path tree of some binary repository management system."""
import datetime as dti
import time
import warnings

from bs4 import BeautifulSoup
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
        else:
            raise ValueError("Must use API token (other authentication means not implemented)")
        self.repositories = {}
        self.repository_map()

    def _fetch(self, url, params=None):
        """DRY."""
        params = {} if not params else params
        self._wait and time.sleep(self._wait)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
            return self._session.get(url, verify=False, params=params)

    def repository_page_links(self, url):
        """Retrieve the repository tree leaf ward links from HTML a tags per tree link (excluding ..)."""
        response = self._fetch(url)
        response.raise_for_status()
        html = response.text
        hrefs = [rel for rel in (tag['href'] for tag in BeautifulSoup(html, "html.parser").find_all("a", href=True)) if not rel.startswith('..')]
        return hrefs

    def repository_map(self):
        """Retrieve the repositories resource and parse into repository dict by key field.
        
        This implementation may or may not work with every BRM on earth ;-)
        """
        repositories_url = f"{self._base_url}repositories/"  # TODO hard coded metadata path
        response = self._fetch(repositories_url)
        response.raise_for_status()
        response_json = response.json()  # TODO depends on JSON type of response
        repo_types_ok = ('LOCAL', 'VIRTUAL')  # TODO specific pass filter - may need adjustment of other installs
        for repository in response_json:  # TODO mapping relies on presence and semantics of key, type,
            key, repo_type = repository.get('key'), repository.get('type')
            if repo_type not in repo_types_ok:
                continue
            self.repositories[key] = {
                "description": repository.get('description'),
                "url": repository.get('url'),  # TODO meaningless entries where url is not given
                "package_type": repository.get('packageType'),
            }



def naive_timestamp(timestamp=None):
    """Logging helper."""
    if timestamp:
        return timestamp.strftime(TS_FORMAT)
    return dti.datetime.now().strftime(TS_FORMAT)

# -*- coding: utf-8 -*-
# pylint: disable=expression-not-assigned,line-too-long
"""Walk the REST accessible path tree of some binary repository management system."""
import datetime as dti
import os
import random
import time
import warnings

from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

DEBUG_VAR = "BRM_DEBUG"
DEBUG = os.getenv(DEBUG_VAR)

ENCODING = "utf-8"
ENCODING_ERRORS_POLICY = "ignore"

BRM_FS_ROOT = "BRM_FS_ROOT"
brm_fs_root = os.getenv(BRM_FS_ROOT, "")
if not brm_fs_root:
    raise RuntimeError(
        f"Please set {BRM_FS_ROOT} to the root of the file system storage like /opt/brm/data/filestore/"
    )

BRM_SERVER = "BRM_SERVER"
brm_server = os.getenv(BRM_SERVER, "")
if not brm_server:
    raise RuntimeError(f"Please set {BRM_SERVER}")

BRM_API_ROOT = "BRM_API_ROOT"
brm_api_root = os.getenv(BRM_API_ROOT, "")
if not brm_api_root:
    raise RuntimeError(f"Please set {BRM_API_ROOT}")

BRM_USER = "BRM_USER"
brm_user = os.getenv(BRM_USER, "")
if not brm_user:
    raise RuntimeError(f"Please set {BRM_USER}")

BRM_TOKEN = "BRM_TOKEN"
brm_token = os.getenv(BRM_TOKEN, "")
if not brm_token:
    raise RuntimeError(f"Please set {BRM_TOKEN}")

TS_FORMAT = "%Y-%m-%d %H:%M:%S"

EDGE = '@e'
NODE = '@n'
HREFS = '@h'
META = '@m'

EASING = True


def easing():
    """Be nice."""
    EASING and time.sleep(random.random() / 1.e5)
    return


def naive_timestamp(timestamp=None):
    """Logging helper."""
    if timestamp:
        return timestamp.strftime(TS_FORMAT)
    return dti.datetime.now().strftime(TS_FORMAT)


def parse_autoindex(page_text):
    """Parse the meta information from the autoindex page given the text."""
    parsed = []
    for line in [t for t in page_text.split('\n') if t.startswith('<a href="')]:
        a, x = line.split('">', 1)
        f, r = x.split('</a>')
        r = r.rstrip()
        d, s, u = r.rsplit(' ', 2)
        d = d.strip()
        parsed.append((f, d, s, u))
    return parsed


def is_node(relative_link):
    """In directory listings a folder is indeicated by a trailing slash (/)."""
    node = not relative_link.endswith('/')
    return node


class TreeWalker:  # pylint: disable=bad-continuation,expression-not-assigned
    """Wrap the auth stuff and the REST BRM tree related walking."""
    
    def __init__(self, server_url, api_root=None, username=None, api_token=None, wait=None):
        self._user_url = server_url.rstrip("/")
        self._base_url = f"{self._user_url}{api_root if api_root else '/'}"
        self._wait = wait if wait else 0.0
        if username and api_token:
            self._session = requests.Session()
            self._session.auth = (username, api_token)
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

    def links(self, url):
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

    def repository_page(self, url):
        """Retrieve the repository tree page and return paths."""
        response = self._fetch(url)
        response.raise_for_status()
        html = response.text
        page_map = {t[0]: t for t in parse_autoindex(html)}
        hrefs = [rel for rel in (tag['href'] for tag in BeautifulSoup(html, "html.parser").find_all("a", href=True)) if not rel.startswith('..')]
        return {HREFS: hrefs, META: page_map}


def trial(argv=None):
    """Drive the tree walker."""
    argv = argv if argv else sys.argv[1:]
    if argv:
        print("ERROR no arguments expected.")
        return 2

    print(f"Job walking REST accessible BRM tree starts at {naive_timestamp()}")
    DEBUG and print(f'Context -> server({brm_server}), API root({brm_api_root}), remote user ({brm_user})')
    walker = TreeWalker(username=brm_user, api_token=brm_token)
    repositories = walker.repository_map()
    print(f"Found {len(repositories)} repositories with interesting types.")
    DEBUG and print(repositories)
    level = 1
    tree = {level: {}}
    for key, repository in repositories.items():
        indent = ""
        DEBUG and print(f"{indent}{key} -> {repository}")
        url = repository["url"]
        data = walker.repository_page(url)
        tree[level][url] = {EDGE: data[HREFS]}
        indent += " " * 2
        print(f"{indent}{url} ->")

        indent += " " * 2
        for url, downward_links in tree[level].items():
            for relative_link in downward_links[EDGE]:
                tree[level][url][relative_link] = {}
                node = is_node(relative_link)
                if not node and relative_link:
                    easing()
                    data = walker.repository_page(f"{url}/{relative_link}")
                    tree[level][url][relative_link][EDGE] = data[HREFS]
                else:
                    data = walker.repository_page(f"{url}")
                    tree[level][url][relative_link][NODE] = {
                        NODE: f"{url}/{relative_link}",
                        META: data[META].get(relative_link, {}),
                    }
                print(f"{indent}{relative_link} {'LEAF' if node else '->'}")

            for relative_link in downward_links[EDGE]:
                for p1 in tree[level][url][relative_link].get(EDGE, []):
                    tree[level][url][relative_link][p1] = {}
                    node = is_node(p1)
                    if not node and relative_link:
                        easing()
                        data = walker.repository_page(f"{url}/{relative_link}/{p1}")
                        tree[level][url][relative_link][p1][EDGE] = data[HREFS]
                    else:
                        data = walker.repository_page(f"{url}/{relative_link}")
                        tree[level][url][relative_link][p1][NODE] = {
                            NODE: f"{url}/{relative_link}{p1}",
                            META: data[META].get(p1, {}),
                        }

            for relative_link in downward_links[EDGE]:
                for p1 in tree[level][url][relative_link].get(EDGE, []):
                    for p2 in tree[level][url][relative_link][p1].get(EDGE, []):
                        tree[level][url][relative_link][p1][p2] = {}
                        node = is_node(p2)
                        if not node and relative_link:
                            easing()
                            data = walker.repository_page(f"{url}/{relative_link}/{p1}/{p2}")
                            tree[level][url][relative_link][p1][p2][EDGE] = data[HREFS]
                        else:
                            data = walker.repository_page(f"{url}/{relative_link}{p1}")
                            tree[level][url][relative_link][p1][p2][NODE] = {
                                NODE: f"{url}/{relative_link}{p1}{p2}",
                                META: data[META].get(p2, {}),
                            }

            for relative_link in downward_links[EDGE]:
                for p1 in tree[level][url][relative_link].get(EDGE, []):
                    for p2 in tree[level][url][relative_link][p1].get(EDGE, []):
                        for p3 in tree[level][url][relative_link][p1][p2].get(EDGE, []):
                            tree[level][url][relative_link][p1][p2][p3] = {}
                            node = is_node(p3)
                            if not node and relative_link:
                                easing()
                                data = walker.repository_page(f"{url}/{relative_link}/{p1}/{p2}/{p3}")
                                tree[level][url][relative_link][p1][p2][p3][EDGE] = data[HREFS]
                            else:
                                data = walker.repository_page(f"{url}/{relative_link}{p1}{p2}")
                                tree[level][url][relative_link][p1][p2][p3][NODE] = {
                                    NODE: f"{url}/{relative_link}{p1}{p2}{p3}",
                                    META: data[META].get(p3, {}),
                                }

            for relative_link in downward_links[EDGE]:
                for p1 in tree[level][url][relative_link].get(EDGE, []):
                    for p2 in tree[level][url][relative_link][p1].get(EDGE, []):
                        for p3 in tree[level][url][relative_link][p1][p2].get(EDGE, []):
                            for p4 in tree[level][url][relative_link][p1][p2][p3].get(EDGE, []):
                                tree[level][url][relative_link][p1][p2][p3][p4] = {}
                                node = is_node(p4)
                                if not node and relative_link:
                                    easing()
                                    data = walker.repository_page(f"{url}/{relative_link}/{p1}/{p2}/{p3}/{p4}")
                                    tree[level][url][relative_link][p1][p2][p3][p4][EDGE] = data[HREFS]
                                else:
                                    data = walker.repository_page(f"{url}/{relative_link}{p1}{p2}{p3}")
                                    tree[level][url][relative_link][p1][p2][p3][NODE] = {
                                        NODE: f"{url}/{relative_link}{p1}{p2}{p3}{p4}",
                                        META: data[META].get(p4, {}),
                                    }

            # for relative_link in downward_links[EDGE]:
            #     for p1 in tree[level][url][relative_link].get(EDGE, []):
            #         for p2 in tree[level][url][relative_link][p1].get(EDGE, []):
            #             for p3 in tree[level][url][relative_link][p1][p2].get(EDGE, []):
            #                 for p4 in tree[level][url][relative_link][p1][p2][p3].get(EDGE, []):
            #                     for p5 in tree[level][url][relative_link][p1][p2][p3][p4].get(EDGE, []):
            #                         tree[level][url][relative_link][p1][p2][p3][p4][p5] = {}
            #                         node = is_node(p5)
            #                         if not node and relative_link:
            #                             easing()
            #                             data = walker.repository_page(f"{url}/{relative_link}/{p1}/{p2}/{p3}/{p4}/{p5}")
            #                             tree[level][url][relative_link][p1][p2][p3][p4][p5][EDGE] = data[HREFS]
            #                         else:
            #                             tree[level][url][relative_link][p1][p2][p3][p4][p5][NODE] = f"{url}/{relative_link}{p1}{p2}{p3}{p4}{p5}"

    with open("tree.json", "wt", encoding=ENCODING) as handle:
        json.dump(tree, handle, indent=2)
    print(f"Job walking REST accessible BRM tree finished at {naive_timestamp()}")
    return 0

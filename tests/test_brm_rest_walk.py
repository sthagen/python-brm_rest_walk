# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import datetime as dti
import pytest  # type: ignore

import responses
import requests

import tests.context as ctx

import brm_rest_walk.brm_rest_walk as brm


def setup():
    ctx.reset()


def test_naive_timestamp_ok_empty_paramter():
    ts = brm.naive_timestamp()
    assert ts.startswith("20")


def test_naive_timestamp_ok_datetime_parameter():
    dt = dti.datetime.now()
    ts = dt.strftime(brm.TS_FORMAT)
    assert brm.naive_timestamp(dt) == ts


def test_tree_walker_nok_missing_user_and_token():
    server = "not_important"
    message = r"Must use API token \(other authentication means not implemented\)"
    with pytest.raises(ValueError, match=message):
        brm.TreeWalker(server)


def test_tree_walker_nok_missing_token():
    server = "not_important"
    message = r"Must use API token \(other authentication means not implemented\)"
    with pytest.raises(ValueError, match=message):
        brm.TreeWalker(server, None, "a_user")


def test_tree_walker_nok_missing_user():
    server = "not_important"
    message = r"Must use API token \(other authentication means not implemented\)"
    with pytest.raises(ValueError, match=message):
        brm.TreeWalker(server, None, username=None, api_token="a_token")


def test_is_node_ok_edge():
    assert brm.is_node('edge/') is False


def test_is_node_ok_node():
    assert brm.is_node('node') is True


def test_easing_ok_no_easing():
    brm.EASING = False
    assert brm.easing() is None  # Call works no timing check


def test_easing_ok_with_easing():
    brm.EASING = True
    assert brm.easing() is None  # Call works no timing check


def test_parse_autoindex_ok_empty():
    assert brm.parse_autoindex('') == []


def test_parse_autoindex_ok_nonsense():
    assert brm.parse_autoindex('There is nothing useful in here') == []


def test_parse_autoindex_nok_start_token_nonsense():
    message = r"not enough values to unpack \(expected 2, got 1\)"
    with pytest.raises(ValueError, match=message):
        brm.parse_autoindex('<a href="There is nothing useful in here')


def test_parse_autoindex_nok_start_token_href_nonsense():
    message = r"not enough values to unpack \(expected 2, got 1\)"
    with pytest.raises(ValueError, match=message):
        brm.parse_autoindex('<a href="maybe">There is nothing useful in here')


def test_parse_autoindex_nok_start_token_href_link_nonsense():
    message = r"not enough values to unpack \(expected 3, got 1\)"
    with pytest.raises(ValueError, match=message):
        brm.parse_autoindex('<a href="maybe">link</a>There_is_still_nothing_useful_in_here_and_no_spaces_to_split_on')


def test_parse_autoindex_ok_minimal():
    f, d, s, u = 'a.txt', '22-Aug-2019 09:53', '2.50', 'MB'
    page_text = f'<a href="{f}">a.txt</a>       {d}  {s} {u}'
    assert brm.parse_autoindex(page_text) == [(f, d, s, u)]


@responses.activate
def test_meta_equests_and_mock_responses_simple():
    responses.add(responses.GET, 'http://example.com/api/1/foobar',
                  json={'error': 'not found'}, status=404)

    resp = requests.get('http://example.com/api/1/foobar')

    assert resp.json() == {"error": "not found"}

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == 'http://example.com/api/1/foobar'
    assert responses.calls[0].response.text == '{"error": "not found"}'


@responses.activate
def test_tree_walker_ok_init():
    repositories = [
        {
            'key': '1',
            'type': 'LOCAL',
            'description': 'describing me',
            'url': 'asdasd',
            'packageType': 'packageType value',
        }
    ]
    serialized_repositories = (
        '[{"key": "1", "type": "LOCAL", "description": "describing me", "url": '
        '"asdasd", "packageType": "packageType value"}]'
    )
    base_url = ctx.BRM_SERVER.rstrip('/')
    api_base_url = f'{base_url}{ctx.BRM_API_ROOT}'
    repositories_url = f'{base_url}{ctx.BRM_API_ROOT}repositories/'
    responses.add(responses.GET, base_url,
                  json={'go': 'ahead'}, status=200)
    responses.add(responses.GET, api_base_url,
                  json={'api': 'found'}, status=200)
    responses.add(responses.GET, repositories_url,
                  json=repositories, status=200)

    walker = brm.TreeWalker(server_url=brm.brm_server, api_root=brm.brm_api_root, username=brm.brm_user, api_token=brm.brm_token)

    assert walker is not None

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == repositories_url
    assert responses.calls[0].response.text == serialized_repositories


@responses.activate
def test_tree_walker_ok_repositories():
    repositories_in = [
        {
            'key': '1',
            'type': 'LOCAL',
            'description': 'describing me',
            'url': 'asdasd',
            'packageType': 'packageType value',
        }
    ]
    serialized_repositories = (
        '[{"key": "1", "type": "LOCAL", "description": "describing me", "url": '
        '"asdasd", "packageType": "packageType value"}]'
    )
    repository_one_digest = {
        '1': {
            'description': 'describing me',
            'package_type': 'packageType value',
            'url': 'asdasd',
        }
    }
    base_url = ctx.BRM_SERVER.rstrip('/')
    api_base_url = f'{base_url}{ctx.BRM_API_ROOT}'
    repositories_url = f'{base_url}{ctx.BRM_API_ROOT}repositories/'
    responses.add(responses.GET, base_url,
                  json={'go': 'ahead'}, status=200)
    responses.add(responses.GET, api_base_url,
                  json={'api': 'found'}, status=200)
    responses.add(responses.GET, repositories_url,
                  json=repositories_in, status=200)

    repositories = brm.TreeWalker(server_url=brm.brm_server, api_root=brm.brm_api_root, username=brm.brm_user, api_token=brm.brm_token).repository_map()
    assert repositories == repository_one_digest


@responses.activate
def test_tree_walker_ok_repositories_ignored():
    repositories_in = [
        {
            'key': '1',
            'type': 'IGNORE',
            'description': 'describing me',
            'url': 'asdasd',
            'packageType': 'packageType value',
        }
    ]
    repository_one_digest = {}
    base_url = ctx.BRM_SERVER.rstrip('/')
    api_base_url = f'{base_url}{ctx.BRM_API_ROOT}'
    repositories_url = f'{base_url}{ctx.BRM_API_ROOT}repositories/'
    responses.add(responses.GET, base_url,
                  json={'go': 'ahead'}, status=200)
    responses.add(responses.GET, api_base_url,
                  json={'api': 'found'}, status=200)
    responses.add(responses.GET, repositories_url,
                  json=repositories_in, status=200)

    repositories = brm.TreeWalker(server_url=brm.brm_server, api_root=brm.brm_api_root, username=brm.brm_user, api_token=brm.brm_token).repository_map()
    assert repositories == repository_one_digest


@responses.activate
def test_tree_walker_ok_links():
    links_page = """\n
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>title</title>
    <link rel="stylesheet" href="style.css">
    <script src="script.js"></script>
  </head>
  <body>
    <a href="f">f</a>       d  s u
  </body>
</html>
    """
    base_url = ctx.BRM_SERVER.rstrip('/')
    api_base_url = f'{base_url}{ctx.BRM_API_ROOT}'
    repositories_url = f'{api_base_url}repositories/'
    links_url = f'{base_url}{ctx.BRM_API_ROOT}links/'

    responses.add(responses.GET, base_url,
                  json={'go': 'ahead'}, status=200)
    responses.add(responses.GET, api_base_url,
                  json={'api': 'found'}, status=200)

    repositories_in = [
        {
            'key': '1',
            'type': 'LOCAL',
            'description': 'describing me',
            'url': f'{api_base_url}data',
            'packageType': 'packageType value',
        }
    ]
    responses.add(responses.GET, repositories_url,
                  json=repositories_in, status=200)
    responses.add(responses.GET, links_url,
                  body=links_page, status=200)
    links = brm.TreeWalker(server_url=brm.brm_server, api_root=brm.brm_api_root, username=brm.brm_user, api_token=brm.brm_token).links(links_url)
    assert links == ['f']


@responses.activate
def test_tree_walker_ok_tree_page():
    base_url = ctx.BRM_SERVER.rstrip('/')
    api_base_url = f'{base_url}{ctx.BRM_API_ROOT}'
    repositories_in = [
        {
            'key': '1',
            'type': 'LOCAL',
            'description': 'describing me',
            'url': f'{api_base_url}data',
            'packageType': 'packageType value',
        }
    ]
    serialized_repositories = (
        '[{"key": "1", "type": "LOCAL", "description": "describing me", "url": '
        f'"{api_base_url}data", "packageType": "packageType value"}}]'
    )
    repository_one_digest = {
        '1': {
            'description': 'describing me',
            'package_type': 'packageType value',
            'url': f'{api_base_url}data',
        }
    }
    repositories_url = f'{api_base_url}repositories/'
    responses.add(responses.GET, base_url,
                  json={'go': 'ahead'}, status=200)
    responses.add(responses.GET, api_base_url,
                  json={'api': 'found'}, status=200)
    responses.add(responses.GET, repositories_url,
                  json=repositories_in, status=200)

    f1, d1, s1, u1 = 'a.txt', '22-Aug-2019 09:53', '2.50', 'MB'
    f2, d2, s2, u2 = 'b/', '22-Aug-2020 09:53', '1.23', 'kB'
    page_a_text = (
        f'<a href="{f1}">{f1}</a>       {d1}  {s1} {u1}'
        '\n'
        f'<a href="{f2}">{f2}</a>       {d2}  {s2} {u2}'
    )
    responses.add(responses.GET, repository_one_digest['1']['url'],
                  body=page_a_text, status=200)

    f3, d3, s3, u3 = 'b.txt', '22-Aug-2020 09:53', '1.23', 'kB'
    page_b_text = (
        f'<a href="{f3}">{f3}</a>       {d3}  {s3} {u3}'
        '\n'
        'we ignore this'
    )

    responses.add(responses.GET, f"{repository_one_digest['1']['url']}/b/",
                  body=page_b_text, status=200)
    expected_tree = {
        1: {
            'https://example.com/api/data': {
                '@e': ['a.txt', 'b/'],
                'a.txt': {
                    '@n': {
                        '@m': (
                            'a.txt',
                            '22-Aug-2019 09:53',
                            '2.50',
                            'MB'
                        ),
                        '@n': 'https://example.com/api/data/a.txt'
                    }
                },
                'b/': {
                    '@e': ['b.txt']
                }
            }
        }
    }
    walker = brm.TreeWalker(server_url=brm.brm_server, api_root=brm.brm_api_root, username=brm.brm_user, api_token=brm.brm_token)
    assert walker is not None
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == repositories_url
    assert responses.calls[0].response.text == serialized_repositories
    repositories = walker.repository_map()
    assert repositories
    level = 1
    tree = {level: {}}
    for key, repository in repositories.items():
        url = repository["url"]
        data = walker.repository_page(url)
        tree[level][url] = {brm.EDGE: data[brm.HREFS]}
        for url, downward_links in tree[level].items():
            for relative_link in downward_links[brm.EDGE]:
                tree[level][url][relative_link] = {}
                node = brm.is_node(relative_link)
                if not node and relative_link:
                    brm.easing()
                    data = walker.repository_page(f"{url}/{relative_link}")
                    tree[level][url][relative_link][brm.EDGE] = data[brm.HREFS]
                else:
                    data = walker.repository_page(f"{url}")
                    tree[level][url][relative_link][brm.NODE] = {
                        brm.NODE: f"{url}/{relative_link}",
                        brm.META: data[brm.META].get(relative_link, {}),
                    }
    assert tree == expected_tree

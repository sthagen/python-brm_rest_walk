# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import datetime as dti
import pytest  # type: ignore

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

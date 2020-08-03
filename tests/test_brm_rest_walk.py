# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import datetime as dti
import pytest  # type: ignore

import brm_rest_walk.brm_rest_walk as brm 


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

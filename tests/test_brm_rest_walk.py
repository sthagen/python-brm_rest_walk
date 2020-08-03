# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import pytest  # type: ignore

import brm_rest_walk.brm_rest_walk as brm 


def test_naive_timestamp_ok_empty_paramter():
    ts = brm.naive_timestamp()
    assert ts.startswith("20")

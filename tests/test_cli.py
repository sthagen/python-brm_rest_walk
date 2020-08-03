# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring,unused-import,reimported
import json
import pytest  # type: ignore

import brm_rest_walk.cli as cli


def test_main_ok_empty_array():
    job = ['[]']
    assert cli.main(job) is None

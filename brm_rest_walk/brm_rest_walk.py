# -*- coding: utf-8 -*-
# pylint: disable=expression-not-assigned,line-too-long
"""Walk the REST accessible path tree of some binary repository management system."""
import datetime as dti

TS_FORMAT = "%Y-%m-%d %H:%M:%S"


def naive_timestamp(timestamp=None):
    """Logging helper."""
    if timestamp:
        return timestamp.strftime(TS_FORMAT)
    return dti.datetime.now().strftime(TS_FORMAT)

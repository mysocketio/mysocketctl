from sys import version_info
from time import time

import jwt
from unittest.mock import mock_open


def make_jwt():
    return jwt.encode({"user_id": "A", "exp": time() + 24 * 60 * 60}, "NotSecret")


def iterable_mock_open(mock=None, read_data=""):
    m = mock_open(mock=mock, read_data=read_data)
    handle = m()
    if version_info.major == 3 and version_info.minor == 6:  # hasattr(handle, "__iter__"):
        # Patching for python 3.6...
        def _side_effect():
            yield from [
                read_data,
            ]

        handle.__iter__.side_effect = _side_effect
    m.reset_mock()
    return m

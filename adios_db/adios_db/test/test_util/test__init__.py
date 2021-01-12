"""
tests for utilities

these test the ones in the __init__.py
"""

import pytest
from adios_db import util


@pytest.mark.parametrize("val, num_figs, expected",
                         [(12345678, 3, 12300000),
                          (123456.78, 2, 120000),
                          (12.345678, 4, 12.35),
                          (123.45678, 2, 120.0),
                          (0.00012345, 2, 0.00012),
                          (-0.00012345, 3, -0.000123),
                          (1.234567e3, 4, 1.235e3),
                          ])
def test_round_sigfigs(val, num_figs, expected):
    assert util.sigfigs(val, num_figs) == expected

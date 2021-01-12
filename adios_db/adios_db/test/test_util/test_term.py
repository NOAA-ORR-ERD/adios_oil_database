import pytest

from adios_db.util.term import TermColor


class TestTermColor(object):
    @pytest.mark.parametrize('color, begin, end',
                             [
                              ('purple', '\033[95m', '\033[0m'),
                              ('cyan', '\033[96m', '\033[0m'),
                              ('darkcyan', '\033[36m', '\033[0m'),
                              ('blue', '\033[94m', '\033[0m'),
                              ('green', '\033[92m', '\033[0m'),
                              ('yellow', '\033[93m', '\033[0m'),
                              ('red', '\033[91m', '\033[0m'),
                              ('bold', '\033[1m', '\033[0m'),
                              ('underline', '\033[4m', '\033[0m'),
                              ])
    def test_term_colors(self, color, begin, end):
        color_string = TermColor.change('hello terminal', color)

        assert color_string.startswith(begin)
        assert color_string.endswith(end)

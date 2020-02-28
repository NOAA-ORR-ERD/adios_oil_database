# Testing the validation framework

import pytest
from oil_database.models.common.validators import (EnumValidator,
                                                   )
from oil_database.models.oil.validation import WARNINGS, ERRORS


class Test_EnumValidator():

    def test_init(self):
        val = EnumValidator(["this", "That"], "W003")

        assert True

    @pytest.mark.parametrize("item", ["this",
                                      "That"])
    def test_valid(self, item):
        val = EnumValidator(["this", "That"], WARNINGS['W003'])
        assert val(item) == []

    @pytest.mark.parametrize("item, expected", [("thi", []),
                                                ("that", []),
                                                ])
    def test_invalid(self, item, expected):
        val = EnumValidator(["this", "That", "the other"], "item: {}, the list: {}")
        result = val(item)
        print(result)
        assert "item" in result[0]
        assert "['this', 'That', 'the other']" in result[0]

    @pytest.mark.parametrize("item", ["tHis",
                                      "thAt"])
    def test_valid_case_insensitive(self, item):
        val = EnumValidator(["this", "That"], WARNINGS['W003'], case_insensitive=True)
        result = val(item)
        print(result)
        assert result == []






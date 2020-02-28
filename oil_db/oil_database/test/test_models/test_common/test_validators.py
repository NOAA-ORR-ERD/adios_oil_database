# Testing the validation framework

import pytest
from oil_database.models.common.validators import (EnumValidator,
                                                   )


class Test_EnumValidator():

    def test_init(self):
        val = EnumValidator(["this", "That"])

        assert True

    @pytest.mark.parametrize("item", ["this",
                                      "That"])
    def test_valid(self, item):
        val = EnumValidator(["this", "That"])
        assert val(item) == []

    @pytest.mark.parametrize("item, expected", [("thi", []),
                                                ("that", []),
                                                ])
    def test_invalid(self, item, expected):
        val = EnumValidator(["this", "That", "the other"])
        result = val(item)
        print(result)
        assert False


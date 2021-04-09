# Testing the validation framework

import pytest
from adios_db.models.common.validators import (EnumValidator,
                                                   FloatRangeValidator,
                                                   YearValidator,
                                                   )

from adios_db.models.oil.validation.warnings import WARNINGS
from adios_db.models.oil.validation.errors import ERRORS


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

    @pytest.mark.parametrize("item, expected", [("thi", []),
                                                ("thats", []),
                                                (None, []),
                                                ])
    def test_invalid_case_insensitive(self, item, expected):
        val = EnumValidator(["this", "That", "the other"],
                            "item: {}, the list: {}",
                            case_insensitive=True)
        result = val(item)
        print(result)
        assert "item" in result[0]


    @pytest.mark.parametrize("item", ["tHis",
                                      "thAt"])
    def test_valid_case_insensitive(self, item):
        val = EnumValidator(["this", "That"], WARNINGS['W003'], case_insensitive=True)
        result = val(item)
        print(result)
        assert result == []

    def test_numbers_good(self):
        val = EnumValidator([3, 5, 7], "Number: {} not one of {}")

        result = val(5)

        assert result == []

    @pytest.mark.parametrize("item", [2,
                                      "a string",
                                      (1, 2, 3),
                                      ])
    def test_numbers_bad(self, item):
        val = EnumValidator([3, 5, 7], "Number: {} not one of {}")

        result = val(item)
        print(result)
        assert len(result) == 1
        assert result[0].startswith('Number:')
        assert str(item) in result[0]


class TestFloatRangeValidator:

    @pytest.mark.parametrize("min, max, value", [(0, 100, 0),
                                                 (0, 100, 100),
                                                 (0, 100, 50),
                                                 ])
    def test_valid(self, min, max, value):
        val = FloatRangeValidator(min, max)

        result = val(value)
        assert result == []

    @pytest.mark.parametrize("min, max, value", [(0, 100, -1),
                                                 (0, 100, 101),
                                                 (0, 100, "this"),
                                                 ])
    def test_invalid(self, min, max, value):
        val = FloatRangeValidator(min, max)

        result = val(value)
        print("result", result)
        assert len(result) == 1
        assert result[0].startswith('ValidationError:')# ' 101 is not between 0 and 100')
        assert str(value) in result[0]
        assert str(min) in result[0]
        assert str(max) in result[0]

class TestYearValidator:

    @pytest.mark.parametrize("min, max, value", [(1700, 2050, 1700),
                                                 (1700, 2050, 2050),
                                                 (1700, 2050, 2020),
                                                 (1700, 2050, "1965"),
                                                 ])
    def test_valid(self, min, max, value):
        val = YearValidator(min, max)

        result = val(value)
        assert result == []

    @pytest.mark.parametrize("min, max, value", [(1700, 2050, 1699),
                                                 (1700, 2050, 2051),
                                                 (1700, 2050, "20-20"),
                                                 ])
    def test_invalid(self, min, max, value):
        val = YearValidator(min, max)

        result = val(value)
        print("result", result)
        assert len(result) == 1
        assert result[0].startswith('ValidationError:')# ' 101 is not between 0 and 100')
        assert str(value) in result[0]
        assert str(min) in result[0]
        assert str(max) in result[0]



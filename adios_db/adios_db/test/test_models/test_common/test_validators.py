"""
Testing the validation framework
"""
import pytest

from adios_db.models.common.validators import (EnumValidator,
                                               FloatRangeValidator,
                                               YearValidator,
                                               DateTimeValidator,
                                               )
from adios_db.models.oil.validation.warnings import WARNINGS


class Test_EnumValidator():
    def test_init(self):
        _val = EnumValidator(["this", "That"], "W003")

        assert True

    @pytest.mark.parametrize("item", ["this", "That"])
    def test_valid(self, item):
        val = EnumValidator(["this", "That"], WARNINGS['W003'])
        assert val(item) == []

    @pytest.mark.parametrize("item, expected", [("thi", []),
                                                ("that", []),
                                                ])
    def test_invalid(self, item, expected):
        val = EnumValidator(["this", "That", "the other"],
                            "item: {}, the list: {}")
        result = val(item)

        assert "item" in result[0]
        assert "['That', 'the other', 'this']" in result[0]

    @pytest.mark.parametrize("item, expected", [("thi", []),
                                                ("thats", []),
                                                (None, []),
                                                ])
    def test_invalid_case_insensitive(self, item, expected):
        val = EnumValidator(["this", "That", "the other"],
                            "item: {}, the list: {}",
                            case_insensitive=True)
        result = val(item)

        assert "item" in result[0]

    @pytest.mark.parametrize("item", ["tHis",
                                      "thAt"])
    def test_valid_case_insensitive(self, item):
        val = EnumValidator(["this", "That"], WARNINGS['W003'],
                            case_insensitive=True)
        result = val(item)

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

        assert len(result) == 1
        assert result[0].startswith('Number:')
        assert str(item) in result[0]


class TestFloatRangeValidator:
    @pytest.mark.parametrize("min_val, max_val, value", [(0, 100, 0),
                                                         (0, 100, 100),
                                                         (0, 100, 50),
                                                         ])
    def test_valid(self, min_val, max_val, value):
        val = FloatRangeValidator(min_val, max_val)

        result = val(value)
        assert result == []

    @pytest.mark.parametrize("min_val, max_val, value", [(0, 100, -1),
                                                         (0, 100, 101),
                                                         (0, 100, "this"),
                                                         ])
    def test_invalid(self, min_val, max_val, value):
        val = FloatRangeValidator(min_val, max_val)

        result = val(value)
        print("result", result)
        assert len(result) == 1

        # ' 101 is not between 0 and 100')
        assert result[0].startswith('ValidationError:')

        assert str(value) in result[0]
        assert str(min_val) in result[0]
        assert str(max_val) in result[0]


class TestYearValidator:
    @pytest.mark.parametrize("min_val, max_val, value", [(1700, 2050, 1700),
                                                         (1700, 2050, 2050),
                                                         (1700, 2050, 2020),
                                                         (1700, 2050, "1965"),
                                                         ])
    def test_valid(self, min_val, max_val, value):
        val = YearValidator(min_val, max_val)

        result = val(value)
        assert result == []

    @pytest.mark.parametrize("min_val, max_val, value", [(1700, 2050, 1699),
                                                         (1700, 2050, 2051),
                                                         (1700, 2050, "20-20"),
                                                         ])
    def test_invalid(self, min_val, max_val, value):
        val = YearValidator(min_val, max_val)

        result = val(value)
        print("result", result)
        assert len(result) == 1

        # ' 101 is not between 0 and 100')
        assert result[0].startswith('ValidationError:')

        assert str(value) in result[0]
        assert str(min_val) in result[0]
        assert str(max_val) in result[0]


class TestDateTimeValidator:
    @pytest.mark.parametrize("value", ["2025-12-04",
                                       "2025-12-04 12:00",
                                       "2025-12-04T12:00",
                                       ])
    def test_valid(self, value):
        val = DateTimeValidator()

        result = val(value)
        assert result == []

    @pytest.mark.parametrize("value", ["2025-24-04",
                                       "2025-12-04 garbage ",
                                       "2025-12-04Time 12:00",
                                       ])
    def test_invalid(self, value):
        val = DateTimeValidator()

        result = val(value)
        assert len(result) == 1
        assert f'"{value}"' in result[0]

        # custom_message:
        val = DateTimeValidator(err_msg="custom: {}")

        result = val(value)
        assert len(result) == 1
        assert result[0] == f"custom: {value}"


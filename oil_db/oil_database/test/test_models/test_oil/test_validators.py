# Testing the validation framework


from oil_database.models.common.validators import (EnumValidator,
                                                   )


class Test_EnumValidator():

    def test_init():
        val = EnumValidator(["this", "That"])

        assert True


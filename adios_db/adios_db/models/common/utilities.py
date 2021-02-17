"""
Tools for helping make our data models.

So far: making dataclasses read/writable as JSON
"""


def something(val):
    '''
        much like python's "Truthy" and Falsey", but we want some values
        to not be false like zero, for instance
    '''
    return ((val == 0) or (val is not None) and val)


def dataclass_to_json(cls):
    """
    class decorator that adds the ability to save a dataclass as JSON

    All fields must be either JSON-able Python types or
    have be a type with a _to_json method
    """

    @classmethod
    def from_py_json(cls, py_json, allow_none=False):
        """
        classmethod to create a dataclass from json compatible python data
        structure.
        """
        arg_dict = {}

        if py_json is None and allow_none is True:
            # the parent object defined an attribute with a default of None
            # We could actually allow other default types, but this one is common
            return py_json

        for fieldname, fieldobj in cls.__dataclass_fields__.items():
            if fieldname in py_json:
                allow_none = True if fieldobj.default is None else False

                try:  # see if it's "one of ours"
                    arg_dict[fieldname] = (fieldobj.type
                                           .from_py_json(py_json[fieldname],
                                                         allow_none=allow_none))
                except AttributeError:
                    # it's not, so we just use the value
                    arg_dict[fieldname] = py_json[fieldname]
                except TypeError:
                    raise TypeError(f'TypeError in {cls.__name__}._from_py_json(): '
                                    f'field: {fieldname}')

        obj = cls(**arg_dict)
        return obj

    def py_json(self, sparse=True):
        """
        function to convert a dataclass to json compatible python

        :param sparse=True: If sparse is True, only non-empty fields will be
                            written. If False, then all fields will be included.

        NOTE: could we use the dataclasses built-in .asdict?
              It would not support sparse.
        """
        json_obj = {}
        for fieldname in self.__dataclass_fields__.keys():
            val = getattr(self, fieldname)
            try:  # convert to json
                val = val.py_json(sparse=sparse)
            except AttributeError:
                pass

            if not sparse:
                json_obj[fieldname] = val
            elif something(val):
                json_obj[fieldname] = val

        return json_obj


    def validate(self):
        """
        Function to validate a dataclass with fields that have validate methods.

        The validate methods are expected to return a list of validation messages.

        The top-level validator extends the existing list
        """
        # print("validate called in: ", type(self))

        # first see if there is a "private" one:
        try:
            messages = self._validate()
        except AttributeError:
            messages = []

        for fieldname, fieldobj in self.__dataclass_fields__.items():
            value = getattr(self, fieldname)
            # print(f"trying to validate: {fieldname} with value: {repr(value)}")
            try:
                # validate with the type's validate method
                messages.extend(fieldobj.type.validate(value))
            except AttributeError:  # This one doesn't have a validate method.
                pass

        # print(f"in {type(self)} -- messages:\n", messages)
        return messages

    def __setattr__(self, name, val):
        try:
            _fieldobj = self.__dataclass_fields__[name]
        except KeyError:
            raise AttributeError(f"You can only set existing attributes: "
                                 f"{self.__class__.__name__}.{name} "
                                 "does not exist")
        self.__dict__[name] = val

    cls.py_json = py_json
    cls.from_py_json = from_py_json
    if hasattr(cls, "validate"):
        cls._validate = cls.validate
    cls.validate = validate
    cls.__setattr__ = __setattr__

    return cls


class JSON_List(list):
    """
    just like a list, but with the ability to turn it into JSON

    A regular list can only be converted to JSON if it has
    JSON-able objects in it.

    Note: must be subclassed, and the item_type attribute set
    """
    item_type = None

    def py_json(self, sparse=True):
        json_obj = []
        for item in self:
            try:
                json_obj.append(item.py_json(sparse))
            except AttributeError:
                json_obj.append(item)

        return json_obj

    @classmethod
    def from_py_json(cls, py_json, allow_none=False):
        """
        create a JSON_List from json array of objects
        that may be json-able.
        """
        if cls.item_type is None:
            raise TypeError("You can not reconstruct a list of unknown type")

        jl = cls()  # an empty JSON_List

        # loop through contents
        for item in py_json:
            jl.append(cls.item_type.from_py_json(item))

        return jl

    def __repr__(self):
        return f"{self.__class__.__name__}({list.__repr__(self)})"


    # def __str__(self):
    #     # why don't either of this work? it's using this repr ??
    #     # return super().__str__()
    #     # return list.__str__(self)


# def dataclass_to_json(cls):
#     """
#     class decorator that adds the ability to save a dataclass as JSON

#     All fields must be either JSON-able Python types or
#     have be a type with a _to_json method
#     """
#     cls.py_json = _py_json
#     cls.from_py_json = _from_py_json
#     cls.validate = _validate
#     cls.__setattr__ = __setattr__

#     return cls

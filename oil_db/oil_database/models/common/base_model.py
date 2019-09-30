#
# Model class definitions for our category object
#
import json
from bson import ObjectId

from pydantic import BaseModel
from typing import Any, Optional, Callable, Union, cast

from oil_database.util.decamelize import camelcase_to_underscore


class PydObjectId(ObjectId):
    '''
        Basically this is the bson ObjectId that has Pydantic validation
        methods added to it.
    '''
    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return v

    @classmethod
    def __get_validators__(cls):
        yield cls.validate


class MongoBaseModel(BaseModel):
    '''
        This is basically the Pydantic BaseModel class overloaded with methods
        that make it easier for such data objects to interact with a PyMongo
        object database.

        In this project, instead of defining classes derived from BaseModel,
        we will derive them from this class.

        Future: Right now, we set the collection as a class attribute.
                This is sorta necessary since the Pydantic data classes
                define their field list with self.__dict__ and enforce it.
                But this means that all instances of a data class will be
                pointing to the same PyMongo collection.
                It is conceivable that some instances would want to point to
                a collection in a particular database, and others would want
                to point to a different one.
    '''
    class Config:
            json_encoders = {
                ObjectId: lambda v: str(v)
            }

    @classmethod
    def attach(cls, db):
        if db is not None:
            if ('__collection__' in cls.__dict__ and
                    cls.__collection__ is not None):
                print('Warning: collection name already set for class {}, '
                      'but we will set it anyway'
                      .format(cls.__name__))
            else:
                collection_name = camelcase_to_underscore(cls.__name__,
                                                          lower=True)
                cls.__collection__ = getattr(db, collection_name)

    def expand(self, name):
        '''
            Lots of attributes will reference an external document by ID.
            This is a helper method to grab those documents
        '''
        attr = getattr(self, name)

        if isinstance(attr, ObjectId):
            return self.find_one(filter={'_id': attr})
        if (isinstance(attr, list) and
                all([isinstance(i, ObjectId) for i in attr])):
            return [self.find_one(filter={'_id': i})
                    for i in attr]
        else:
            return attr

    def __setattr__(self, name, value):
        '''
            Are there any dataclass packages that don't have at least one
            annoyance?
            pydantic doesn't accept attributes as fields if they start with
            an underscore.
            This sucks for PyMongo, since the default identifier is _id
        '''
        if name == '_id':
            self.__dict__[name] = value
        else:
            super().__setattr__(name, value)

    #
    # Here are some helper methods specific to handling PyMongo
    #
    def get_collection(self):
        if hasattr(self.__class__, '__collection__'):
            return self.__class__.__collection__
        else:
            return None

    def expanded_ref_attrs(self):
        attrs = {}

        collection = self.get_collection()
        if collection is None:
            return attrs

        for k in self.fields:
            attr = getattr(self, k)

            if isinstance(attr, ObjectId):
                attrs[k] = collection.find_one({'_id': attr})
            elif (isinstance(attr, list) and
                    any([isinstance(i, ObjectId) for i in attr])):
                attrs[k] = [collection.find_one({'_id': i})
                            for i in attr]

        return attrs

    def dict(self, *, expand_refs=False, **kwargs) -> 'DictStrAny':
        '''
            Overloaded version of BaseModel.dict(), which adds the
            expand_refs argument.
        '''
        res = super().dict(**kwargs)
        res['_cls'] = '{}.{}'.format(self.__class__.__module__,
                                     self.__class__.__name__)

        if (expand_refs is True and
                self.get_collection() is not None):
            expanded_attrs = self.expanded_ref_attrs()
            res.update(expanded_attrs)

        return res

    def json(self, *,
             include: Union['SetIntStr', 'DictIntStrAny'] = None,
             exclude: Union['SetIntStr', 'DictIntStrAny'] = None,
             by_alias: bool = False,
             skip_defaults: bool = False,
             encoder: Optional[Callable[[Any], Any]] = None,
             **dumps_kwargs: Any
             ) -> str:
        '''
            Overloaded version of BaseModel.json(), which adds the
            expand_refs argument.
        '''
        encoder = cast(Callable[[Any], Any], encoder or self._json_encoder)
        expand_refs = dumps_kwargs.pop('expand_refs', False)

        return json.dumps(self.dict(include=include, exclude=exclude,
                                    by_alias=by_alias,
                                    skip_defaults=skip_defaults,
                                    expand_refs=expand_refs),
                          default=encoder,
                          **dumps_kwargs)

    def save(self):
        if '_id' not in self.__dict__ or self._id is None:
            self.insert()
        else:
            self.replace()

        return self

    def insert(self):
        self._id = self.get_collection().insert_one(self.dict()).inserted_id

    def replace(self):
        self.get_collection().replace_one({'_id': self._id},
                                          self.dict(),
                                          upsert=True)

    @classmethod
    def find(cls, **kwargs):
        res = cls.__collection__.find(**kwargs)
        ret = []

        for kwargs in res:
            ret.append(cls(**kwargs))
            ret[-1]._id = kwargs['_id']

        return ret

    @classmethod
    def find_one(cls, *args, **kwargs):
        res = cls.__collection__.find_one(*args, **kwargs)

        ret = cls(**res)
        ret._id = res['_id']

        return ret

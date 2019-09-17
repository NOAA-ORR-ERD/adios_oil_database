from pymodm import EmbeddedDocumentField


class EmbeddedMongoModelMixin(object):
    def _set_embedded_property_args(self, kwargs):
        '''
            Here, we handle the arguments that contain embedded documents.
        '''
        for attr, value in self.__class__.__dict__.items():
            if (isinstance(value, EmbeddedDocumentField) and
                    attr in kwargs and
                    kwargs[attr] is not None):
                embedded_model = value.related_model

                if isinstance(kwargs[attr], dict):
                    #print('create {} from kwargs: {}'
                    #      .format(embedded_model.__name__, kwargs[attr]))

                    kwargs[attr] = embedded_model(**kwargs[attr])

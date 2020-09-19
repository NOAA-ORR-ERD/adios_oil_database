# The Oil Database Session object
from numbers import Number

from pymongo import MongoClient


class Session():
    def __init__(self, host, port, database):
        self.mongo_client = MongoClient(host=host, port=port)

        self.db = getattr(self.mongo_client, database)
        self.oil = self.db.oil  # the oil collection

    def query(self, oil_id=None, text=None, api=None, labels=None,
              **kwargs):
        '''
            The Mongodb find() function has a bunch of parameters, but we are
            mainly interested in find(filter=None, projection=None), where:
            - filter: The filtering terms
            - projection: The field names to be returned

            query options:
            - oil_id: The identifier of a specific record
            - text: A string that is matched against the oil name, location.
                    The matching will be case insensitive.
            - api: A range of numbers in which the API of the oil will be
                   filtered.
            - labels: A list of label strings that will be matched against the
                      oil labels to filter the results.
        '''
        filter_opts = {}
        filter_opts.update(self.id_arg(oil_id))
        filter_opts.update(self.text_arg(text))
        filter_opts.update(self.api_arg(api))
        filter_opts.update(self.labels_arg(labels))

        projection = kwargs.get('projection', None)

        return self.oil.find(filter=filter_opts, projection=projection)

    def id_arg(self, obj_id):
        return {} if obj_id is None else {'_id': obj_id}

    def name_arg(self, name):
        if name is None:
            return {}
        else:
            return {'metadata.name': {'$regex': name, '$options': 'i'}}

    def location_arg(self, location):
        if location is None:
            return {}
        else:
            return {'metadata.location': {'$regex': location, '$options': 'i'}}

    def text_arg(self, text_to_match):
        if text_to_match is None:
            return {}
        else:
            return self.make_inclusive([self.name_arg(text_to_match),
                                        self.location_arg(text_to_match)])

    def api_arg(self, apis):
        '''
            apis can be a number, string, or list
            - If it is a number, we will assume it is a minimum api
            - If it is a list length 1, we will assume it is a minimum api
            - If it is a list greater than 2, we will only use the first 2
              elements as a min/max
            - If it is a string, we will try to parse it as a set of comma
              separated values.
        '''
        if apis is None:
            return {}
        elif isinstance(apis, Number):
            low, high = apis, None
        elif isinstance(apis, str):
            try:
                apis = [float(a) for a in apis.split(',')]
            except Exception:
                # something non-numeric was passed in
                apis = [None, None]

            low = apis[0]
            high = None if len(apis) < 2 else apis[1]
        else:
            # assume it is a list
            low = None if len(apis) < 1 else apis[0]
            high = None if len(apis) < 2 else apis[1]

        if low is not None and high is not None:
            if low > high:
                low, high = high, low

            return {'metadata.API': {'$gte': low, '$lte': high}}
        elif low is not None:
            return {'metadata.API': {'$gte': low}}
        elif high is not None:
            return {'metadata.API': {'$lte': high}}

    def labels_arg(self, labels):
        if labels is None:
            labels = []
        elif isinstance(labels, str):
            labels = [l.strip() for l in labels.split(',')]

        if len(labels) == 1:
            return {'metadata.labels': {'$in': labels}}
        elif len(labels) > 1:
            return self.make_exclusive([{'metadata.labels': {'$in': [l]}}
                                        for l in labels])
        else:
            return {}

    def make_inclusive(self, opts):
        '''
            Normally, the filtering options will be exclusive, i. e. if we are
            searching on name='alaska' and location='north', we would only get
            records that satisfy both criteria (criteria are AND'd together).
            Setting the options to inclusive would yield records that satisfy
            any of the criteria (OR'd together).
        '''
        if isinstance(opts, dict):
            return {'$or': [dict([i]) for i in opts.items()]}
        else:
            return {'$or': opts}

    def make_exclusive(self, opts):
        '''
            Normally, the filtering options will be exclusive, i. e. if we are
            searching on name='alaska' and location='north', we would only get
            records that satisfy both criteria (criteria are AND'd together).

            This is fine for filtering criteria that have unique names.  But
            sometimes we want multiple criteria for a single name, such as
            when we want all items in a list to match another list.  In such
            cases, we need to AND them explicitly.
        '''
        if isinstance(opts, dict):
            return {'$and': [dict([i]) for i in opts.items()]}
        else:
            return {'$and': opts}

    def __getattr__(self, name):
        '''
            Any referenced attributes that are not explicitly defined in this
            class will be assumed to belong to the mongo client.  So we will
            pass them down.
        '''
        return getattr(self.mongo_client, name)

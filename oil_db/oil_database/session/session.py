# The Oil Database Session object
from pymongo import MongoClient, mongo_client


class Session():
    def __init__(self, host, port, database):
        self.mongo_client = MongoClient(host=host, port=port)

        self.db = getattr(self.mongo_client, database)
        self.oil = self.db.oil  # the oil collection

    def query(self, ignore_case=False, inclusive=False, **kwargs):
        '''
            The Mongodb find() function has a bunch of parameters, but we are
            mainly interested in find(filter=None, projection=None), where:
            - filter: The filtering terms
            - projection: The field names to be returned
        '''
        filter_opts = kwargs.get('filter', {})
        filter_opts.update(self.id_arg(kwargs.get('id', None)))
        filter_opts.update(self.name_arg(kwargs.get('name', None),
                                         ignore_case))
        filter_opts.update(self.location_arg(kwargs.get('location', None),
                                             ignore_case))

        projection = kwargs.get('projection', None)

        if inclusive:
            filter_opts = self.make_opts_inclusive(filter_opts)

        return self.oil.find(filter=filter_opts, projection=projection)

    def id_arg(self, obj_id):
        if obj_id is None:
            return {}
        else:
            return {'_id': obj_id}

    def name_arg(self, name, ignore_case):
        if name is None:
            return {}
        else:
            ret = {'metadata.name': {'$regex': name}}

            if ignore_case:
                ret['metadata.name']['$options'] = 'i'

            return ret

    def location_arg(self, location, ignore_case):
        if location is None:
            return {}
        else:
            ret = {'metadata.location': {'$regex': location}}

            if ignore_case:
                ret['metadata.location']['$options'] = 'i'

            return ret

    def make_opts_inclusive(self, opts):
        '''
            Normally, the filtering options will be exclusive, i. e. if we are
            searching on name='alaska' and location='north', we would only get
            records that satisfy both criteria (criteria are AND'd together).
            Setting the options to inclusive would yield records that satisfy
            any of the criteria (OR'd together).
        '''
        return {"$or": [dict([i]) for i in opts.items()]}

    def __getattr__(self, name):
        '''
            Any referenced attributes that are not explicitly defined in this
            class will be assumed to belong to the mongo client.  So we will
            pass them down.
        '''
        return getattr(self.mongo_client, name)










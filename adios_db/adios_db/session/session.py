# The Oil Database Session object
from numbers import Number
import warnings
from pymongo import MongoClient, ASCENDING, DESCENDING

from ..models.oil.product_type import types_to_labels


class CursorWrapper():
    '''
        Wraps a mongodb cursor to provide an iterator that we can do some
        filtering on, while not losing all its methods

        At this point, all it's doing is removing the _id key

        Seems like a lot of effort for that, but the alternative is to realize
        the entire thing into a list -- which may be a bad idea.

        Rant: why doesn't a mongo cursor have a __len__ rather than using
              .count() to make it more like a regular Sequence?

              oh, and now count() is deprecated as well!
    '''
    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self):
        self.cursor = iter(self.cursor)
        return self

    def __next__(self):
        obj = next(self.cursor)
        obj.pop('_id', None)
        return obj

    def __len__(self):
        return self.cursor.count()

    def __getitem__(self, idx):
        return self.cursor[idx]

    # def count(self, *args, **kwargs):
    #     return self.cursor.count(*args, **kwargs)

    def __getattr__(self, attr):
        """
        Pass anything else on to the embedded cursor

        Just in case -- we really should document whats being used.
        """
        warnings.warn("ideally, we should not be using mongo "
                      "cursor methods directly."
                      f": `{attr}` Should be wrapped somehow",
                      DeprecationWarning)

        return getattr(self.cursor, attr)


class Session():

    sort_direction = {'asc': ASCENDING,
                      'ascending': ASCENDING,
                      'desc': DESCENDING,
                      'descending': DESCENDING}

    def __init__(self, host, port, database):
        """
        Initialize a mongodb backed session

        :param host: hostname of mongo server
        :param port: port of mongo server
        :param database: database name used for this data.
        """
        self.mongo_client = MongoClient(host=host, port=port)

        self.db = getattr(self.mongo_client, database)
        self.oil = self.db.oil  # the oil collection

    def query(self, oil_id=None,
              text=None, api=None, labels=None, product_type=None,
              gnome_suitable=None,
              sort=None, sort_case_sensitive=False, page=None,
              projection=None,
              **kwargs):
        '''
        Query the database according to various criteria

        :returns: an iterator of dicts (json-compatible) of the data asked for


        Where:

        **Filtering**

          projection:
            The field names to be returned

        **query options:**

            oil_id:
                The identifier of a specific record

            text:
                A string that is matched against the oil name, location.
                The matching will be case insensitive.

            api:
                A range of numbers in which the API of the oil will be
                filtered.

            labels:
                A list of label strings that will be matched against the
                oil labels to filter the results.

            gnome_suitable:
                A Flag (True|False) that will be matched against the oil's
                gnome_suitable boolean field to filter the results.  A None
                value means do not filter.

        **sort options:** A list of options consisting of ('field_name',
                                                           'direction')

            field_name:
                The name of a field to be used for sorting.  Dotted
                notation can be used to specify fields within fields.

            direction:
                Specifies whether to sort in ascending or descending
                order. Can be any of::

                     {'asc',
                      'ascending',
                      'desc',
                      'descending'}

        The Mongodb find() function has a bunch of parameters, but we are
        mainly interested in ``find(filter=None, orderby, projection=None)``

        .. note::

            MongoDB 3.6 has changed how they compare array fields in a
            sort. It used to compare the arrays element-by-element,
            continuing until any "ties" were broken.  Now it only
            compares the highest/lowest valued element, apparently
            ignoring the rest.

            Reference: https://docs.mongodb.com/manual/release-notes/3.6-compatibility/#array-sort-behavior

            For this reason, a MongoDB query will not properly sort our
            status and labels array fields, at least not in a simple way.

        '''
        filter_opts = self.filter_options(oil_id, text, api, labels,
                                          product_type, gnome_suitable)

        sort = self.sort_options(sort)

        if projection is not None:
            # make sure we always get the oil_id
            projection = ['oil_id'] + list(projection)
        ret = self.oil.find(filter=filter_opts, projection=projection)

        if sort is not None:
            if sort_case_sensitive is False:
                ret = ret.collation({'locale': 'en'})

            ret = ret.sort(sort)

        start, stop = self.parse_interval_arg(page)

        return CursorWrapper(ret[start:stop])

    def filter_options(self, oil_id, text, api, labels, product_type,
                       gnome_suitable):
        filter_opts = {}
        filter_opts.update(self.id_arg(oil_id))
        filter_opts.update(self.text_arg(text))
        filter_opts.update(self.api_arg(api))
        filter_opts.update(self.product_type_arg(product_type))
        filter_opts.update(self.labels_arg(labels))
        filter_opts.update(self.gnome_suitable_arg(gnome_suitable))

        return filter_opts

    def sort_options(self, sort):
        if sort is None:
            return sort
        else:
            return [(opt[0], self.sort_direction.get(opt[1], ASCENDING))
                    for opt in sort]

    def id_arg(self, obj_id):
        return {} if obj_id is None else {'oil_id': obj_id}

    def id_filter_arg(self, obj_id):
        if obj_id is None:
            return {}
        else:
            return {'oil_id': {'$regex': obj_id, '$options': 'i'}}

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

    def alternate_names_arg(self, name):
        if name is None:
            return {}
        else:
            return {'metadata.alternate_names': {'$elemMatch': {
                '$regex': name, '$options': 'i'
            }}}

    def text_arg(self, text_to_match):
        if text_to_match is None:
            return {}
        else:
            ret = []

            for w in text_to_match.split():
                ret.append(self.make_inclusive([self.id_filter_arg(w),
                                                self.name_arg(w),
                                                self.location_arg(w),
                                                self.alternate_names_arg(w)]))

            ret = self.make_exclusive(ret)

            return ret

    def api_arg(self, apis):
        low, high = self.parse_interval_arg(apis)

        if low is not None and high is not None:
            return {'metadata.API': {'$gte': low, '$lte': high}}
        elif low is not None:
            return {'metadata.API': {'$gte': low}}
        elif high is not None:
            return {'metadata.API': {'$lte': high}}
        else:
            return {}

    def product_type_arg(self, product_type):
        if product_type is None:
            return {}
        else:
            return {'metadata.product_type': product_type}

    def labels_arg(self, labels):
        if labels is None:
            labels = []
        elif isinstance(labels, str):
            labels = [l.strip() for l in labels.split(',')]

        if len(labels) == 1:
            return {'metadata.labels': {'$in': labels}}
        elif len(labels) > 1:
            return self.make_inclusive([{'metadata.labels': {'$in': [l]}}
                                        for l in labels])
        else:
            return {}

    def gnome_suitable_arg(self, gnome_suitable):
        if gnome_suitable is None:
            return {}
        else:
            try:
                gnome_suitable = gnome_suitable.lower() in ('true', '1')
            except AttributeError:
                gnome_suitable = bool(gnome_suitable)

            return {'metadata.gnome_suitable': {'$exists': True,
                                                '$eq': gnome_suitable}}

    def parse_interval_arg(self, interval):
        '''
        An interval argument can be a number, string, or list

        - If it is a number, we will assume it is a minimum

        - If it is a list length 1, we will assume it is a minimum

        - If it is a list greater than 2, we will only use the first 2
          elements as a min/max

        - If it is a string, we will try to parse it as a set of comma
          separated values.
        '''
        if interval is None:
            low, high = None, None
        elif isinstance(interval, Number):
            low, high = interval, None
        elif isinstance(interval, str):
            try:
                interval = [float(i) for i in interval.split(',')]
            except Exception:
                # something non-numeric was passed in
                interval = [None, None]

            low = interval[0]
            high = None if len(interval) < 2 else interval[1]
        else:
            # assume it is a list
            low = None if len(interval) < 1 else interval[0]
            high = None if len(interval) < 2 else interval[1]

        if low is not None and high is not None:
            if low > high:
                low, high = high, low

        return low, high

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
            Normally, the filtering options will be exclusive, i.e. if we are
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

    def get_labels(self, identifier=None):
        '''
            Right now we are getting labels and associated product types
            from the adios_db model code.  But it would be better managed
            if we eventually migrate this to labels stored in a database
            collection.
        '''
        # get the whole list of labels
        labels = [{'name': label, 'product_types': sorted(types)}
                  for (label, types) in types_to_labels.product_types.items()]

        # so it's at least somewhat consistent, we sort and then enumerate
        # our labels
        labels.sort(key=lambda i: i['name'])

        for idx, obj in enumerate(labels):
            obj['_id'] = idx

        if identifier is None:
            return labels
        else:
            try:
                identifier = int(identifier)
            except ValueError as e:
                e.args = ('label identifiers are integer only',)
                raise

            # get a single label
            label = [i for i in labels if i['_id'] == identifier]

            return label[0] if len(label) > 0 else None

    def insert_oil_record(self, oil, overwrite=False):
        """
        add a new oil record to the oil collection

        :param oil: an Oil object to add

        :param overwrite=False: whether to overwrite an existing
                                record if it already exists.
        """
        obj = oil.py_json()

        self.oil.insert_one(obj)

    def __getattr__(self, name):
        # FixMe: This should be fully hiding the mongo client
        #        so probably should NOT do this!
        '''
            Any referenced attributes that are not explicitly defined in this
            class will be assumed to belong to the mongo client.  So we will
            pass them down.
        '''
        return getattr(self.mongo_client, name)

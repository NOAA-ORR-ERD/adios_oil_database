"""
ADIOS DB Session object

This module encapsulates a MongoDB session for use behind the WebAPI,
or other uses that require high performance querying, etc.

In theory this same Session object could be duck typed to use a
different back-end: RDBMS, simple file store, etc.
"""

from numbers import Number
import warnings

from pymongo import MongoClient, ASCENDING, DESCENDING

from ..models.oil.oil import Oil
from ..models.oil.product_type import types_to_labels
from ..models.oil.completeness import set_completeness


class CursorWrapper():
    '''
    Wraps a mongodb cursor to provide an iterator that we can do some
    filtering on, while not losing all its methods

    At this point, all it's doing is removing the _id key

    Seems like a lot of effort for that, but the alternative is to realize
    the entire thing into a list -- which may be a bad idea.

    Rant-- Why doesn't a mongo cursor have a __len__ rather than using
    .count() to make it more like a regular Sequence?

    oh, and now ``count()`` is deprecated as well, but I haven't
    figured out what to replace it with.
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

        Just in case -- we really should document what's being used.
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
        '''
            Initialize a mongodb backed session

            :param host: hostname of mongo server
            :param port: port of mongo server
            :param database: database name used for this data.
        '''
        self.mongo_client = MongoClient(host=host, port=port)

        self._db = getattr(self.mongo_client, database)
        self._oil_collection = self._db.oil  # the oil collection

    def get_oil(self, oil_id):
        """
        get an oil record by its ID from the oil collection

        :param oil_id: an Oil ID
        """
        rec = self._oil_collection.find_one({'oil_id': oil_id})
        # remove the mongo ID
        if rec is not None:
            rec.pop('_id', None)
        return rec

    def delete_oil(self, oil_id):
        '''
        Delete an oil record from the oil collection.

        :param oil_id: an Oil identifier
        '''
        return self._oil_collection.delete_one({'oil_id': oil_id}).deleted_count

    def insert_oil(self, oil):
        '''
            Add a new oil record to the oil collection

            :param oil: an Oil object to add

            :param overwrite=False: whether to overwrite an existing
                                    record if it already exists.
        '''
        if isinstance(oil, Oil):
            if oil.oil_id in ('', None):
                oil.oil_id = self.new_oil_id()
        else:
            # assume a json object
            if ('oil_id' not in oil or
                    oil['oil_id'] in ('', None)):
                oil['oil_id'] = self.new_oil_id()

            oil = Oil.from_py_json(oil)

        oil.reset_validation()
        set_completeness(oil)

        json_obj = oil.py_json()
        json_obj['_id'] = oil.oil_id

        inserted_id = self._oil_collection.insert_one(json_obj).inserted_id
        assert inserted_id == oil.oil_id

        return json_obj

    def new_oil_id(self, id_prefix='XX'):
        """
        Query the database for the next highest ID with the given prefix.

        The current implementation is to walk the oil IDs, filter for the
        prefix, and choose the max numeric content.

        :param id_prefix='XX': The ID prefix to use. Each prefix is code
            that indicates something about the source. IDs are a two
            letter code followed by 5 digits with leading zeros. "XX"
            is the default for records of unknown provenance

        *Warning:* We don't expect a lot of traffic POST'ing a bunch new oils to
        the database, it will only happen once in awhile. But this is not the
        most effective way to do this. A persistent incremental counter would
        be much faster. In fact, this is a bit brittle, and would fail if the
        website suffered a bunch of POST requests at once.
        """
        max_seq = 0

        cursor = (self._oil_collection
                  .find({'oil_id': {'$regex': '^{}'.format(id_prefix)}},
                        {'oil_id'}))

        for row in cursor:
            oil_id = row['oil_id']

    def find_one(self, oil_id):
        ret = self._oil_collection.find_one({'oil_id': oil_id})

        if ret is not None:
            ret.pop('_id', None)

        return ret

    def insert_one(self, oil_obj):
        if isinstance(oil_obj, Oil):
            oil_obj = oil_obj.py_json()

        if not hasattr(oil_obj, '_id'):
            oil_obj['_id'] = oil_obj['oil_id']

        return self._oil_collection.insert_one(oil_obj).inserted_id

    def replace_one(self, oil_obj):
        if isinstance(oil_obj, Oil):
            oil_obj = oil_obj.py_json()

        return self._oil_collection.replace_one({'oil_id': oil_obj['oil_id']},
                                    oil_obj)

    def delete_one(self, oil_id):
        return self._oil_collection.delete_one({'oil_id': oil_id})

    def new_oil_id(self):
        '''
            Query the database for the next highest ID with a prefix of XX
            The current implementation is to walk the oil IDs, filter for the
            prefix, and choose the max numeric content.

            Warning: We don't expect a lot of traffic POST'ing a bunch new oils
                     to the database, it will only happen once in awhile.
                     But this is not the most effective way to do this.
                     A persistent incremental counter would be much faster.
                     In fact, this is a bit brittle, and would fail if the
                     website suffered a bunch of POST requests at once.
        '''
        id_prefix = 'XX'
        max_seq = 0

        cursor = (self._oil_collection.find({'oil_id': {'$regex': f'^{id_prefix}'}},
                                {'oil_id'}))

        for row in cursor:
            oil_id = row['oil_id']

            try:
                oil_seq = int(oil_id[len(id_prefix):])
            except ValueError:
                print('ValuError: continuing...')
                continue

            max_seq = oil_seq if oil_seq > max_seq else max_seq

        max_seq += 1  # next in the sequence

        return f'{id_prefix}{max_seq:06d}'

    def query(self, oil_id=None,
              text=None, api=None, labels=None, product_type=None,
              gnome_suitable=None,
              sort=None,
              sort_case_sensitive=False,
              page=None,
              projection=None,
              ):
        '''
        Query the database according to various criteria

        :returns: an iterator of dicts (json-compatible) of the data asked for


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

        **sort options:**

        A list of options consisting of ``('field_name', 'direction')``

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
        filter_opts = self._filter_options(oil_id, text, api, labels,
                                           product_type, gnome_suitable)

        sort = self._sort_options(sort)

        if projection is not None:
            # make sure we always get the oil_id
            projection = ['oil_id'] + list(projection)

        ret = self._oil_collection.find(filter=filter_opts, projection=projection)

        if sort is not None:
            if sort_case_sensitive is False:
                ret = ret.collation({'locale': 'en'})

            ret = ret.sort(sort)

        start, stop = self._parse_interval_arg(page)

        return CursorWrapper(ret[start:stop])

    def _sort_options(self, sort):
        if sort is None:
            return sort
        else:
            return [(opt[0], self.sort_direction.get(opt[1], ASCENDING))
                    for opt in sort]

    def _filter_options(self, oil_id, text, api, labels, product_type,
                        gnome_suitable):
        filter_opts = {}
        filter_opts.update(self._id_arg(oil_id))
        filter_opts.update(self._text_arg(text))
        filter_opts.update(self._api_arg(api))
        filter_opts.update(self._product_type_arg(product_type))
        filter_opts.update(self._labels_arg(labels))
        filter_opts.update(self._gnome_suitable_arg(gnome_suitable))

        return filter_opts

    def _id_arg(self, obj_id):
        return {} if obj_id is None else {'oil_id': obj_id}

    def _api_arg(self, apis):
        low, high = self._parse_interval_arg(apis)

        if low is not None and high is not None:
            return {'metadata.API': {'$gte': low, '$lte': high}}
        elif low is not None:
            return {'metadata.API': {'$gte': low}}
        elif high is not None:
            return {'metadata.API': {'$lte': high}}
        else:
            return {}

    def _product_type_arg(self, product_type):
        if product_type is None:
            return {}
        else:
            return {'metadata.product_type': product_type}

    def _labels_arg(self, labels):
        if labels is None:
            labels = []
        elif isinstance(labels, str):
            labels = [l.strip() for l in labels.split(',')]

        if len(labels) == 1:
            return {'metadata.labels': {'$in': labels}}
        elif len(labels) > 1:
            return self._make_inclusive([{'metadata.labels': {'$in': [l]}}
                                        for l in labels])
        else:
            return {}

    def _gnome_suitable_arg(self, gnome_suitable):
        if gnome_suitable is None:
            return {}
        else:
            try:
                gnome_suitable = gnome_suitable.lower() in ('true', '1')
            except AttributeError:
                gnome_suitable = bool(gnome_suitable)

            return {'metadata.gnome_suitable': {'$exists': True,
                                                '$eq': gnome_suitable}}

    def _text_arg(self, text_to_match):
        if text_to_match is None:
            return {}
        else:
            ret = []

            for w in text_to_match.split():
                ret.append(self._make_inclusive([self._id_filter_arg(w),
                                                self._name_arg(w),
                                                self._location_arg(w),
                                                self._alternate_names_arg(w)]))

            ret = self._make_exclusive(ret)

            return ret

    def _id_filter_arg(self, obj_id):
        if obj_id is None:
            return {}
        else:
            return {'oil_id': {'$regex': obj_id, '$options': 'i'}}

    def _name_arg(self, name):
        if name is None:
            return {}
        else:
            return {'metadata.name': {'$regex': name, '$options': 'i'}}

    def _location_arg(self, location):
        if location is None:
            return {}
        else:
            return {'metadata.location': {'$regex': location, '$options': 'i'}}

    def _alternate_names_arg(self, name):
        if name is None:
            return {}
        else:
            return {'metadata.alternate_names': {'$elemMatch': {
                '$regex': name, '$options': 'i'
            }}}

    def _parse_interval_arg(self, interval):
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

    def _make_inclusive(self, opts):
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

    def _make_exclusive(self, opts):
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
        labels = types_to_labels.all_labels_dict

        if identifier is None:
            return labels
        else:
            msg = 'label identifiers are integer >= 0 only'
            try:
                identifier = int(identifier)
            except ValueError as e:
                raise ValueError(msg) from e
            if identifier < 0:
                raise ValueError(msg)

            # Get a single label
            for label in labels:
                if label['_id'] == identifier:
                    return label
            return None

    def __getattr__(self, name):
        # FixMe: This should be fully hiding the mongo client
        #        so probably should NOT do this!
        '''
            Any referenced attributes that are not explicitly defined in this
            class will be assumed to belong to the mongo client.  So we will
            pass them down.
        '''
        return getattr(self.mongo_client, name)

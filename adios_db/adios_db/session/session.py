"""
ADIOS DB Session object

This module encapsulates a MongoDB session for use behind the WebAPI,
or other uses that require high performance querying, etc.

In theory this same Session object could be duck typed to use a
different back-end: RDBMS, simple file store, etc.
"""
from pathlib import Path
from numbers import Number
import warnings
import mimetypes

from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
from gridfs import GridFS

from ..models.oil.product_type import types_to_labels


# The MIME type of an XLSX file could be missing on our docker images,
# so we manually add it here.
mimetypes.add_type(
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xlsx'
)


class CursorWrapper():
    """
    Wraps a mongodb cursor to provide an iterator that we can do some
    filtering on, while not losing all its methods

    At this point, all it's doing is removing the _id key

    Seems like a lot of effort for that, but the alternative is to realize
    the entire thing into a list -- which may be a bad idea.

    Rant-- Why doesn't a mongo cursor have a __len__ rather than using
    .count() to make it more like a regular Sequence?

    oh, and now ``count()`` is deprecated as well.
    """
    def __init__(self, cursor):
        self.cursor = cursor

    def __iter__(self):
        # this is do-nothing, a cursor is already an iterator
        # -- but just in case.
        self.cursor = iter(self.cursor)
        return self

    def __next__(self):
        obj = next(self.cursor)
        obj.pop('_id', None)
        return obj

    def __len__(self):
        try:
            return self.cursor.explain()['executionStats']['nReturned']
        except StopIteration:
            # explain() does this when the cursor has zero items
            return 0

    def __getitem__(self, idx):
        return self.cursor[idx]


class OpenFileObjectContext:
    """
    This is a context manager usable in a 'with' block that takes an already
    open file.  This is so we define some actions upon entering & exiting
    the context.
    """
    def __init__(self, file_obj):
        if not callable(getattr(file_obj, 'read', None)):
            raise ValueError(f'"{type(file_obj).__name__}" '
                             'object has no callable attribute "read"')

        self.file_obj = file_obj

    def __enter__(self):
        return self.file_obj

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.file_obj.flush()  # flush, but do not close
        return False  # Re-raise any exceptions


class Attachments():
    """
    We sometimes get spectroscopic and Gas Chromatography(GC) data, as well as
    other interesting and relevant things, in document form, which are related
    to a particular oil but external to its oil record assay.  So we have a
    problem trying to add this data to the Adios Oil schema.  And this could
    happen more often in the future.  For example, all the new LSU analysis
    data.

    These are usually simply PDFs or images, but we don't want to limit
    ourselves.

    We deal with this by formalizing the collection of arbitrary file
    attachments that are stored and associated with an oil record.
    """
    def __init__(self, database):
        self._bucket = GridFS(database, "attachments")

    @property
    def _collection(self):
        try:
            return self._bucket._collection
        except AttributeError:
            # use the old API
            return self._bucket._GridFS__collection

    @property
    def _files(self):
        try:
            return self._bucket._files
        except AttributeError:
            # use the old API
            return self._bucket._GridFS__files

    @property
    def bucket_name(self):
        return self._collection.name

    def attachment_file_path(self, oil_id, file_path):
        """
        Here is the spec we came up with for the final storage of attachment
        files in the noaa-oil-data Git repo.

            f'data/{collection}/{prefix}/{oil_id}/{id}'

        where:
            collection == 'attachments'
            prefix == {oil_id[:2]}
            oil_id == {the_oil_identifier}
            id == {the_document_filename}

        So we will just match the stuff below the collection, such that
        the path will be formatted as:

            f'{prefix}/{oil_id}/{id}'

        I know this spec is probably too specific for general attachments
        functionality, but if it becomes a problem, we can maybe split the
        file path spec functionality between adios_db and web_api
        """
        try:
            filename = Path(file_path).name
        except TypeError:
            filename = ''

        return f'{oil_id[:2]}/{oil_id}/{filename}'

    def get_content_type(self, file_path):
        """
        Right now we are just using the builtin mimetypes package, which just
        looks at the file extension and compares it to the mime.types entries
        installed on your operating system.  This should recognize most of the
        common types.

        A better way would be to use python-magic.  python-magic is a Python
        interface to the libmagic file type identification library.
        Libmagic is a library that identifies file types by examining their
        content rather than relying solely on file extensions.
        It's the underlying technology behind the Unix file command
        """
        mime_type, _encoding = mimetypes.guess_type(file_path)
        return mime_type

    def list(self):
        return self._bucket.list()

    def find_oil_attachments(self, oil_id):
        return [
            f._file
            for f in self._bucket.find({
                'filename': {'$regex': f'.+{oil_id}.+'}
            })
        ]

    def find_one(self, oil_id=None, file_path=None, file_id=None):
        """
        Returns a file-like object
        """
        ret = None

        if oil_id is not None and file_path is not None:
            filename = self.attachment_file_path(oil_id, file_path)
            ret = self._bucket.find_one({
                'filename': filename
            })
        elif file_id is not None:
            if not isinstance(file_id, ObjectId):
                file_id = ObjectId(file_id)

            ret = self._bucket.find_one({
                '_id': file_id
            })
        else:
            raise ValueError('Bad values passed in: '
                             f'{oil_id=}, {file_path=}, {file_id=}')

        if ret is None:
            raise FileNotFoundError(f'Could not find "{filename}"')

        return ret

    def insert_one(self, oil_id, file_path, file_obj=None, **kwargs):
        """
        We insert a file into MongoDB as a GridFS blob.

        :param oil_id: The ID of the associated oil record
        :param file_path: The path of the file we are inserting.
                          This is NOT assumed to be pointing to a valid file
                          in a local file system.  We do need the name of the
                          file in order to give the inserted blob an
                          identifier though.
        :param file_obj: A readable open file-like object

        Basically the preferred method would be to pass in an open file object.
        But we will "try" to open the file_path if there is none passed in.
        """
        if file_obj is None:
            return self._insert_file_path(oil_id, file_path, **kwargs)
        else:
            return self._insert_file_obj(oil_id, file_path, file_obj, **kwargs)

    def _insert_file_path(self, oil_id, file_path, **kwargs):
        attachment_path = self.attachment_file_path(oil_id, file_path)

        try:
            with open(file_path, 'rb') as file_obj:
                return self._insert_or_replace(
                    attachment_path,
                    self.get_content_type(file_path),
                    file_obj,
                    **kwargs
                )
        except FileNotFoundError:
            raise FileNotFoundError(f'Could not find file "{file_path}" '
                                    'to insert')

    def _insert_file_obj(self, oil_id, file_path, file_obj, **kwargs):
        attachment_path = self.attachment_file_path(oil_id, file_path)

        try:
            with OpenFileObjectContext(file_obj) as file_obj:
                return self._insert_or_replace(
                    attachment_path,
                    self.get_content_type(file_path),
                    file_obj,
                    **kwargs
                )
        except ValueError:
            raise ValueError(f'Could not create context for "{file_obj}" '
                             'to insert')

    def _insert_or_replace(self, attachment_path, content_type, file_obj,
                           **kwargs):
        kwargs = self.gfs_put_prune_kwargs(kwargs)

        # Check if file with same name exists
        existing_file = self._bucket.find_one({
            'filename': attachment_path
        })

        if existing_file:
            obj_id = existing_file._id
            self._bucket.delete(obj_id)

            # Upload new file content re-using the ID
            self._bucket.put(file_obj,
                             _id=obj_id,
                             filename=attachment_path,
                             content_type=content_type,
                             **kwargs)
        else:
            obj_id = self._bucket.put(file_obj,
                                      filename=attachment_path,
                                      content_type=content_type,
                                      **kwargs)

        return obj_id

    def gfs_put_prune_kwargs(self, kwargs):
        """
        Basically when we perform a gfs put() operation, we want to pass any
        custom fields that we find in our kwargs.  But we don't want to use
        any keywords that are reserved for GridFS.  I imagine that we could
        do better than a hard-coded list of keys, but this will do for now.
        """
        forbidden_keys = {'_id', 'filename', 'length', 'contentType',
                          'chunkSize', 'uploadDate'}

        return {k: v
                for k, v in kwargs.items()
                if k not in forbidden_keys}

    def replace_one(self, oil_id, file_path, **kwargs):
        """
        This is just to have a similar API to the regular Session object
        for oil record handling.  GridFS doesn't behave exactly like the
        builtin MongoDB collections.
        """
        return self.insert_one(oil_id, file_path, **kwargs)

    def replace_fields(self, oil_id, file_path, **kwargs):
        """
        For a single file, update any extra fields
        without replacing the GridFS file contents.
        """
        if oil_id is not None and file_path is not None:
            filename = self.attachment_file_path(oil_id, file_path)

            set_items = {k: v for k, v in kwargs.items()
                         if v is not None and v != ''}
            unset_items = {k: v for k, v in kwargs.items()
                           if v is None or v == ''}

            return self._files.update_one(
                {'filename': filename},
                {'$set': set_items, '$unset': unset_items},
            )
        else:
            return None

    def get_extra_fields(self, oil_id, file_path):
        """
        For a single file, return any extra fields it is storing.
        """
        if oil_id is not None and file_path is not None:
            filename = self.attachment_file_path(oil_id, file_path)

            return self.gfs_put_prune_kwargs(
                self._files.find_one(
                    {'filename': filename},
                )
            )
        else:
            return None

    def delete_one(self, oil_id, file_path):
        """
        Delete a single File with the given oil_id & filename.
        Deletes of non-existent files are considered successful so we always
        return None
        """
        attachment_path = self.attachment_file_path(oil_id, file_path)

        existing = self._bucket.find_one({'filename': attachment_path})

        if existing:
            obj_id = existing._id
            return self._bucket.delete(obj_id)
        else:
            return None


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
        self.server_info = self.mongo_client.server_info()

        self._db = getattr(self.mongo_client, database)
        self._oil_collection = self._db.oil
        self.attachments = Attachments(self._db)

    def find_one(self, oil_id):
        """
        return a single Oil object from the collection
        """
        ret = self._oil_collection.find_one({'oil_id': oil_id})

        if ret is not None:
            ret.pop('_id', None)

        return ret

    def insert_one(self, oil_obj):
        """
        add a new Oil to the collection
        """
        oil_id = oil_obj.oil_id
        oil_obj = oil_obj.py_json()

        oil_obj['_id'] = oil_id

        self._oil_collection.insert_one(oil_obj)

        return oil_id

    def replace_one(self, oil_obj):
        """
        replace existing Oil object with the same oil_id
        """
        oil_obj = oil_obj.py_json()

        return self._oil_collection.replace_one({'oil_id': oil_obj['oil_id']},
                                                oil_obj)

    def delete_one(self, oil_id):
        """
        delete a single Oil object with the given oil_id
        """
        return self._oil_collection.delete_one({'oil_id': oil_id})

    def new_oil_id(self, id_prefix='XX'):
        """
        Query the database for the next highest ID with the provided
        prefix.

        :param id_prefix = 'XX': Prefix of new ID

        The current implementation is to walk the oil IDs, filter for the
        prefix, and choose the max numeric content.

        Warning: We don't expect a lot of traffic POST'ing a bunch new oils
                 to the database, it will only happen once in awhile.
                 But this is not the most effective way to do this.
                 A persistent incremental counter would be much faster.
                 In fact, this is a bit brittle, and would fail if the
                 website suffered a bunch of POST requests at once.
        """
        max_seq = 0

        cursor = self._oil_collection.find(
            {'oil_id': {'$regex': f'^{id_prefix}'}},
            {'oil_id'}
        )

        for row in cursor:
            oil_id = row['oil_id']

            try:
                oil_seq = int(oil_id[len(id_prefix):])
            except ValueError:
                print('ValuError: continuing...')
                continue

            max_seq = oil_seq if oil_seq > max_seq else max_seq

        max_seq += 1  # next in the sequence

        return f'{id_prefix}{max_seq:05d}'

    def query(self,
              oil_id=None,
              text=None,
              api=None,
              labels=None,
              product_type=None,
              gnome_suitable=None,
              sort=None,
              sort_case_sensitive=False,
              page=None,
              projection=None,
              ):
        """
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
        """
        filter_opts = self._filter_options(oil_id, text, api, labels,
                                           product_type, gnome_suitable)

        sort = self._sort_options(sort)

        if projection is not None:
            # make sure we always get the oil_id
            projection = ['oil_id'] + list(projection)

        ret = self._oil_collection.find(filter=filter_opts,
                                        projection=projection)

        if sort is not None:
            if sort_case_sensitive is False:
                ret = ret.collation({'locale': 'en'})

            ret = ret.sort(sort)

        start, stop = self._parse_interval_arg(page)

        total_results = ret.explain()['executionStats']['nReturned']

        return (CursorWrapper(ret[start:stop]), total_results)

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
            labels = [label.strip() for label in labels.split(',')]

        if len(labels) == 1:
            return {'metadata.labels': {'$in': labels}}
        elif len(labels) > 1:
            return self._make_inclusive(
                [{'metadata.labels': {'$in': [label]}}
                 for label in labels]
            )
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
                ret.append(self._make_inclusive([
                    self._id_filter_arg(w),
                    self._name_arg(w),
                    self._location_arg(w),
                    self._alternate_names_arg(w)
                ]))

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
        """
        An interval argument can be a number, string, or list
        - If it is a number, we will assume it is a minimum
        - If it is a list length 1, we will assume it is a minimum
        - If it is a list greater than 2, we will only use the first 2
          elements as a min/max
        - If it is a string, we will try to parse it as a set of comma
          separated values.
        """
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
        """
        Normally, the filtering options will be exclusive, i. e. if we are
        searching on name='alaska' and location='north', we would only get
        records that satisfy both criteria (criteria are AND'd together).
        Setting the options to inclusive would yield records that satisfy
        any of the criteria (OR'd together).
        """
        if isinstance(opts, dict):
            return {'$or': [dict([i]) for i in opts.items()]}
        else:
            return {'$or': opts}

    def _make_exclusive(self, opts):
        """
        Normally, the filtering options will be exclusive, i.e. if we are
        searching on name='alaska' and location='north', we would only get
        records that satisfy both criteria (criteria are AND'd together).

        This is fine for filtering criteria that have unique names.  But
        sometimes we want multiple criteria for a single name, such as
        when we want all items in a list to match another list.  In such
        cases, we need to AND them explicitly.
        """
        if isinstance(opts, dict):
            return {'$and': [dict([i]) for i in opts.items()]}
        else:
            return {'$and': opts}

    def get_labels(self, identifier=None):
        """
        Right now we are getting labels and associated product types
        from the adios_db model code.  But it would be better managed
        if we eventually migrate this to labels stored in a database
        collection.
        """
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

    def list_database_names(self):
        return self.mongo_client.list_database_names()

    def drop_database(self, db_name):
        return self.mongo_client.drop_database(db_name)

    def get_database(self, db_name):
        return getattr(self.mongo_client, db_name)

    @property
    def address(self):
        return self.mongo_client.address

    def __getattr__(self, name):
        """
        Any referenced attributes that are not explicitly defined in this
        class will be assumed to belong to the mongo client.  So we will
        pass them down.

        FixMe: This should be fully hiding the mongo client
               so probably should NOT do this!
        """
        warnings.warn("Using mongo methods directly is deprecated. "
                      f"`{name}` functionality should be added to the "
                      "Session class",
                      DeprecationWarning)
        return getattr(self.mongo_client, name)

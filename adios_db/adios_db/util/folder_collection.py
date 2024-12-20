import json
import pathlib


class FolderCollection:
    """
    Ducktyped class that acts like a MongoDB oil collection, but acts upon a
    file folder instead.

    The file folder is assumed to be a base folder, and we will assume the
    filesystem structure is that of the noaa-oil-data project.
    As such, the oil records are saved in a path like:

    `f'{folder}/oil/{oil_id_prefix}/{oil_id}.json'`
    """
    def __init__(self, folder):
        folder = pathlib.Path(folder)

        if folder.is_dir():
            self.folder = folder
        else:
            raise ValueError("Path is not a directory")

        self._index_file_ids()

    def _index_file_ids(self):
        self.oil_id_index = {}
        self.next_id = {}

        for file_path in self.folder.glob('**/*.json'):
            prefix = file_path.parts[-2]
            if prefix not in self.oil_id_index:
                self.oil_id_index[prefix] = {}

            if prefix not in self.next_id:
                self.next_id[prefix] = 0

            with open(file_path, encoding="utf-8") as fd:
                oil_json = json.load(fd)
                oil_id = oil_json['oil_id']
                source_id = oil_json['metadata'].get('source_id', None)
                oil_name = oil_json['metadata']['name']

                self.oil_id_index[prefix][(oil_name, source_id)] = oil_id

            self.next_id[prefix] = max(self.next_id[prefix],
                                       int(oil_id.lstrip(prefix)))

    def _next_id(self, prefix):
        try:
            self.next_id[prefix] += 1
        except Exception:
            self.next_id[prefix] = 1

        return f'{prefix}{self.next_id[prefix]:05}'

    def _previous_id(self, prefix, oil_name, source_id):
        """
        look up the previous id that was generated for an oil, or return None
        """
        return (self.oil_id_index.get(prefix, {})
                .get((oil_name, source_id), None))

    def _get_path_and_filename(self, oil_obj):
        oil_id = oil_obj['oil_id']
        oil_id_prefix = oil_id[:2]

        if oil_id_prefix:
            path = self.folder.joinpath('oil', oil_id_prefix)
        else:
            path = self.folder

        return path, f'{oil_id}.json'

    def _file_exists(self, folder, filename):
        return filename in [o.name for o in folder.iterdir()]

    def find_one_and_replace(self, filter, replacement, upsert=True):
        """
        Insert our json record into the filesystem

        For the Exxon records, there is no source field that we can use
        to generate an ID.  Each record does have a unique name however.

        So we generate the IDs in this class using an automated method.
        In the initial case, the IDs start at 0 and increment with each
        subsequent record.

        This poses a problem when re-running the importer with new records
        in the set, because unless the records are processed in exactly
        the same order, it is likely a bunch of records will be saved
        with different IDs than they previously had.

        The solution is to query the filesystem (typically a git repo),
        and build an index associating a record's name with an ID.  This
        will tell us if a particular named oil has had a previous ID.

        - if the named oil has a previous ID, then use it
        - otherwise, generate the next ID and use it.
        """
        oil_name = replacement['metadata']['name']
        source_id = replacement['metadata'].get('source_id', None)

        oil_id = replacement['oil_id']
        prefix = oil_id[:2]

        previous_id = self._previous_id(prefix, oil_name, source_id)
        if previous_id is not None:
            replacement['oil_id'] = previous_id
        else:
            replacement['oil_id'] = self._next_id(prefix)

        #print(f'inserting {replacement["oil_id"]}, '
        #      f'{replacement['metadata'].get('source_id', None)}')

        folder, filename = self._get_path_and_filename(replacement)
        folder.mkdir(exist_ok=True)

        with folder.joinpath(filename).open('w') as fd:
            fd.write(json.dumps(replacement, indent=4))

    def replace_one(self, filter, replacement, upsert=True):
        raise NotImplemented

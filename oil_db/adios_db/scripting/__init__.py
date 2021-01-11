"""
Assorted utilities to help with writing scripts that use the oil database
"""

from pathlib import Path
import json

from oil_database.models.oil.oil import Oil


def get_all_records(data_dir):
    """
    gets all the records from the JSON data stored in gitLab

    This is a generator that gets all the records, returning them one by one
    as record, path pairs

    :param data_dir: the directory that holds the data

    The record returned is an Oil object

    Use as such::
       for oil, path in get_all_records(data_dir):
            work_with_the_record

    """
    dir = Path(data_dir)
    for fname in dir.rglob("*.json"):
        with open(fname, encoding='utf-8') as jfile:
            pyjson = json.load(jfile)
        rec = Oil.from_py_json(pyjson)

        yield rec, fname
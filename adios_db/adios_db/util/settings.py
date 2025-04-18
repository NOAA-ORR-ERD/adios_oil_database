"""
some common methods for getting some application settings
for the oil database
"""
from configparser import ConfigParser


def default_settings():
    return {
        'mongodb.host': 'localhost',
        'mongodb.port': 27017,
        'mongodb.database': 'adios_db',
        'mongodb.alias': 'adios-db-app',
        'gridfs.buckets': ['attachments'],
    }


def file_settings(config_file, section='app:adios_db'):
    config = ConfigParser()
    config.read(config_file)

    settings = {k: convert_str_to_type_value(v) for k, v in config.items(section)}

    for k in ('gridfs.buckets',):
        # these keys contain listable values, separated by '\n'
        settings[k] = settings[k].split('\n')

    return settings


def convert_str_to_type_value(str_in):
    """
    I really don't see why the config parser can't just do this, at least
    as an option.
    It would obviate the need for a utility module like this.
    """
    if str_in in ('True', 'true'):
        return True
    elif str_in in ('False', 'false'):
        return False
    else:
        try:
            return int(str_in)
        except ValueError:
            try:
                return float(str_in)
            except ValueError:
                # default to string if we can't convert to anything
                return str_in

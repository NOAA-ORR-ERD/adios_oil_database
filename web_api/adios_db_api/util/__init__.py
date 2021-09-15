
from bson.objectid import ObjectId

def fix_bson_ids(json_data):
    # FixME: if we don't use the _id field do we need this at all?
    '''
        JSON, specifically the ujson package, is having problems representing
        the BSON special ObjectId fields.  So we need to turn them into
        something representable, like a string, before sending our JSON back
        in a response.
    '''
    if isinstance(json_data, ObjectId):
        return str(json_data)
    elif isinstance(json_data, dict):
        for k, v in json_data.items():
            json_data[k] = fix_bson_ids(v)

        return json_data
    elif isinstance(json_data, (list, tuple)):
        for i, v in enumerate(json_data):
            json_data[i] = fix_bson_ids(v)

        return json_data
    elif isinstance(json_data, set):
        tmp_list = list(json_data)

        for i, v in enumerate(tmp_list):
            tmp_list[i] = fix_bson_ids(v)

        return set(tmp_list)
    else:
        return json_data

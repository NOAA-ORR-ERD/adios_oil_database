
# from bson.objectid import ObjectId


# def fix_bson_ids(json_data):
#     # FixME: if we don't use the _id field do we need this at all?
#     '''
#         JSON, specifically the ujson package, is having problems representing
#         the BSON special ObjectId fields.  So we need to turn them into
#         something representable, like a string, before sending our JSON back
#         in a response.
#     '''
#     if isinstance(json_data, ObjectId):
#         return str(json_data)

#     elif isinstance(json_data, dict):
#         return {k: fix_bson_ids(v) for k, v in json_data.items()}

#     elif isinstance(json_data, (list, tuple)):
#         return [fix_bson_ids(v) for v in json_data]

#     elif isinstance(json_data, set):
#         return {fix_bson_ids(v) for v in json_data}

#     else:
#         return json_data

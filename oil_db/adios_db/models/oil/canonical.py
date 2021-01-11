import copy

def get_new_oil(name, sparse=False):
    """
    returns a new, complete empty oil record, with the name set
    """
    if sparse:
        raise NotImplementedError
    else:
        oil = copy.deepcopy(RECORD_SPEC)
        oil["name"] = name
    return oil


RECORD_SPEC = {"_id": "XX000000",
               "name": "dummy name",
# everything else here
               }

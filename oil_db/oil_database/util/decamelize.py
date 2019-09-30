'''
    utility functions to turn camelcase into discreet separated words.
'''
from itertools import zip_longest


def separate_camelcase(camelcase):
    idxs = [i for i, c in enumerate(camelcase) if c.isupper()]

    return [camelcase[begin:end]
            for (begin, end) in zip_longest(idxs, idxs[1:])]


def camelcase_to_sep(camelcase, sep=' ', lower=False):
    ret = sep.join(separate_camelcase(camelcase))

    if lower:
        return ret.lower()
    else:
        return ret


def camelcase_to_space(camelcase, lower=False):
    return camelcase_to_sep(camelcase, lower=lower)


def camelcase_to_underscore(camelcase, lower=False):
    return camelcase_to_sep(camelcase, sep='_', lower=lower)

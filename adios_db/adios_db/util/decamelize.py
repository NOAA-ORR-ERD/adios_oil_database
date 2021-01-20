'''
    utility functions to turn camelcase into discreet separated words.
'''
from itertools import zip_longest


def separate_camelcase(camelcase):
    idxs = [i for i, c in enumerate(camelcase) if c.isupper()]

    words = [camelcase[begin:end]
             for (begin, end) in zip_longest(idxs, idxs[1:])]

    return _concatenate_single_letters(words)


def _concatenate_single_letters(words):
    res = []
    prev = ''

    for w in words:
        if len(w) > 1:
            if len(prev) > 0:
                res.append(prev)
                prev = ''

            res.append(w)
        else:
            prev += w

    if len(prev) > 0:
        res.append(prev)

    return res


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

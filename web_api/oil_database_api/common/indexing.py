from __future__ import print_function


def iter_keywords(str_in):
    lines = str_in.splitlines()
    in_tr = False
    ret = set()

    for l in lines:
        if in_tr:
            keyword = l.strip().lower()
            ret.add(keyword)

        if "keywords" in l or "keyword" in l:
            in_tr = True
        else:
            in_tr = False

    return ', '.join(sorted(ret))

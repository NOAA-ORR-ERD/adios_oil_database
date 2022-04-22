"""
assorted utilities for querying an Oil object
"""


def get_evaporated_subsample(oil):
    """
    return the first evaporated sub_sample if there is one:
    """
    for ss in oil.sub_samples:
        if (ss.metadata.fraction_evaporated is None or
                ss.metadata.fraction_evaporated.value is None):
            continue

        fe = ss.metadata.fraction_evaporated.converted_to('fraction').value

        # it would be an error if this isn't the case!
        if 0 < fe < 1.0:
            return ss

    return None

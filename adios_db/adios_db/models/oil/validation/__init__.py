

# A list of ERRORS and WARNINGS that we can usually ignore
#  these are ones that we'll probably never be able to fix
ERRORS_TO_IGNORE = {'W000', 'W009'}


def unpack_status(status):
    """
    unpacks the status messages into list of tuples

    (error_code, message
    """
    errors = {}
    for full_msg in status:
        error_code, msg = full_msg.split(":", 1)
        errors.setdefault(error_code, []).append(msg.strip())
    return errors


def is_only_ignored(status):
    """
    Check if all the status codes are ones that are on the ignored list

    expects a dict of teh form returned by unpack_status
    """
    return ERRORS_TO_IGNORE >= status.keys()


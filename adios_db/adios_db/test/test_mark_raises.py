"""
This is just a test of the pytest-raises package.  It is required
in order to parametrize our exceptional behavior.
This will most likely fail if the package has not been installed.
"""
import pytest


class SomeException(Exception):
    pass


class AnotherException(Exception):
    pass


@pytest.mark.parametrize(
    'error',
    [None,
     pytest.param(SomeException('the message'),
                  marks=pytest.mark.raises(SomeException(),
                                           exception=SomeException)),
     pytest.param(AnotherException('the message'),
                  marks=pytest.mark.raises(SomeException(),
                                           exception=AnotherException)),
     pytest.param(Exception('the message'),
                  marks=pytest.mark.raises(exception=Exception)),
     ])
def test_mark_raises(error):
    """
    Note: Okay, this is not the 'official' way to parametrize exceptional
          behavior, but this is how we will do it.  And here's why.

          First, it seems this parametrize list form was valid at one time,
          but now gives the following warning:

            RemovedInPytest4Warning: Applying marks directly to parameters
                                     is deprecated, please use
                                     pytest.param(..., marks=...) instead.

          But replacing it with an equivalent pytest.param is not currently
          possible.  The best we can do is configure an xfail that expects
          a particular exception.

          I do not like this.  If I am expecting a test to raise a
          particular exception and it does in fact raise the exception,
          then I would consider the test to have passed, not 'xfailed'.

          And if I am inspecting a bunch of pytest results (1500+ in some
          cases), it is visually more work to identify which tests are
          xfailing because they expect some kind of failure condition,
          and which ones are xfailing because they are not implemented yet.

          So we will suffer a bunch of warnings as a better alternative to
          suffering a bunch of expected xfails.  And we will deal with
          pytest 4 when the time comes.
    """
    if error:
        raise error

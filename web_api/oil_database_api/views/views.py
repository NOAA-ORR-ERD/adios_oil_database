""" Cornice services.
"""
from cornice import Service


hello = Service(name='hello', path='/', description="Simplest view")


@hello.get()
def get_info(request):
    """Returns Hello in JSON."""
    return {'Hello': ', welcome to the Oil Database API!!'}

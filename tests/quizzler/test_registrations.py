import collections.abc

from quizzler import registrations


def test_load():
    """Make sure the files load.
    """
    mapping = registrations.get_uid_registration_mapping()
    assert isinstance(mapping, collections.abc.Mapping)

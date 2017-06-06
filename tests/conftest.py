import pathlib
import sys


def pytest_sessionstart(session):
    # Add project root to import path.
    sys.path = [
        str(pathlib.Path(__file__).resolve().parent.parent),
    ] + sys.path

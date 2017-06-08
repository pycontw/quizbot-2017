import pytest

from webapi.app import app as flask_app


@pytest.fixture
def app():
    return flask_app

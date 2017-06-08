import pytest


@pytest.fixture
def app():
    from webapi.app import app as flask_app
    return flask_app

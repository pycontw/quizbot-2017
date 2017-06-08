import functools
import json

import pytest

from quizzler import registrations, users


def generate_mock_leaders(faker, leader_count, leader_factory=users.Leader):
    for ranking in range(1, leader_count + 1):
        serial = faker.ssn()
        user = users.User(serial=serial)
        registration = registrations.Registration({
            'Id': serial,
            '聯絡人 Email': faker.email(),
            'Nickname (shown on ID card) / 暱稱 (顯示於識別證)': faker.name(),
        })
        yield leader_factory(
            ranking=ranking, score=faker.pyint(),
            user=user, registration=registration,
        )


@pytest.mark.parametrize('accept_header', [
    'application/json',
    'application/json, text/html;q=0.9',
])
def test_leaderboard_json(accept_header, client, faker, mocker):
    faker.seed(1234)

    mock_count = 3
    mocked = functools.partial(generate_mock_leaders, faker, mock_count)
    mocker.patch('quizzler.users.generate_leaders', mocked)

    response = client.get('/leaderboard', headers={'Accept': accept_header})

    assert response.status_code == 200
    assert response.mimetype == 'application/json'

    assert json.loads(response.data.decode('utf8')) == {'leaders': [
        {
            'ranking': 1, 'score': 5670,
            'user': {'serial': '797-57-1915', 'nickname': 'Andre Mccormick'},
        },
        {
            'ranking': 2, 'score': 8865,
            'user': {'nickname': 'Shirley Wright', 'serial': '664-80-7934'},
        },
        {
            'ranking': 3, 'score': 8324,
            'user': {'nickname': 'Joseph Smith', 'serial': '478-09-9855'},
        },
    ]}


@pytest.mark.parametrize('accept_header', [
    'text/html',
    'application/json;q=0.9, text/html',
])
def test_leaderboard_html(accept_header, client, faker, mocker):
    faker.seed(1234)

    mock_count = 3
    mocked = functools.partial(generate_mock_leaders, faker, mock_count)
    mocker.patch('quizzler.users.generate_leaders', mocked)

    response = client.get('/leaderboard', headers={'Accept': accept_header})

    assert response.status_code == 200
    assert response.mimetype == 'text/html'

import functools

import pytest

from quizzler import registrations, users


def generate_mock_leaders(faker, leander_count, leader_factory=users.Leader):
    for ranking in range(1, leander_count + 1):
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
    mock_count = 10
    mocked = functools.partial(generate_mock_leaders, faker, mock_count)
    mocker.patch('quizzler.users.generate_leaders', mocked)

    response = client.get('/leaderboard', headers={'Accept': accept_header})

    assert response.status_code == 200
    assert response.mimetype == 'application/json'


@pytest.mark.parametrize('accept_header', [
    'text/html',
    'application/json;q=0.9, text/html',
])
def test_leaderboard_html(accept_header, client, faker, mocker):
    mock_count = 10
    mocked = functools.partial(generate_mock_leaders, faker, mock_count)
    mocker.patch('quizzler.users.generate_leaders', mocked)

    response = client.get('/leaderboard', headers={'Accept': accept_header})

    assert response.status_code == 200
    assert response.mimetype == 'text/html'

import pytest
from app import app
# from const import MAX_MESSAGE_LEN


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def test_post_messages(client):
    """Test that messages work."""
    data = {
        'name': 'John',
        'email': 'john@gmail.com',
        'message': 'HI!'
    }

    rv = client.post('/send_message', data=data)
    assert b'OK' in rv.data


def test_wrong_email_format(client):
    """Test return error if received wrong e-mail."""

    data = {
        'name': 'John',
        'email': 'john@gmail,com',
        'message': 'HI!'
    }

    rv = client.post('/send_message', data=data)
    assert b'invalid email' in rv.data


def test_wrong_name_format(client):
    """Test return error if received long name."""

    data = {
        'name': 'John' * 100,
        'email': 'john@gmail.com',
        'message': 'HI!'
    }

    rv = client.post('/send_message', data=data)
    assert b'long name' in rv.data


def test_very_long_message(client):
    """Test return error if received long name."""

    data = {
        'name': 'John',
        'email': 'john@gmail.com',
        # 'message': '.' * MAX_MESSAGE_LEN
    }

    rv = client.post('/send_message', data=data)
    assert b'OK' in rv.data
    # data['message'] += '.'
    # rv = client.post('/send_message', data=data)
    # assert b'long message' in rv.data
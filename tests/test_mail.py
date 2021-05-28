import pytest
import wsgi
from wsgi import run_scrap, mail, create_app
# from const import MAX_MESSAGE_LEN


@pytest.fixture
def client():
    app = create_app(environment="testing")
    app.config['TESTING'] = True

    with app.test_client() as client:
        app_ctx = app.app_context()
        app_ctx.push()
        yield client
        app_ctx.pop()


def test_post_error_messages(client, monkeypatch):
    """Test that messages work."""

    TEST_ERROR_MESSAGE = "TEST Error"

    def mock_data_scrap():
        assert False, TEST_ERROR_MESSAGE

    monkeypatch.setattr(wsgi, "data_scrap", mock_data_scrap)
    with mail.record_messages() as outbox:
        run_scrap()
        assert len(outbox) == 1
        assert TEST_ERROR_MESSAGE in outbox[0].body

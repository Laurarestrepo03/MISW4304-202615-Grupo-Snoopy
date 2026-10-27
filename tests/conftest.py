from unittest.mock import patch

import pytest
import random
from faker import Faker
from flask_jwt_extended import create_access_token
from flask_sqlalchemy import SQLAlchemy

_patcher = patch.object(SQLAlchemy, "create_all")
_patcher.start()

from app import app as flask_app

_patcher.stop()

@pytest.fixture
def app():
    flask_app.config.update(
        TESTING=True,
        JWT_SECRET_KEY="95256083074188200234198418528944" # numero random
    )
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="blacklist-client")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_blacklist(mocker):
    return mocker.patch("resources.blacklist.Blacklist")

@pytest.fixture
def mock_db(mocker):
    return mocker.patch("resources.blacklist.db")

@pytest.fixture(scope="session")
def fake():
    return Faker()

@pytest.fixture
def blacklist_payload(fake):
    return {
        "email": fake.safe_email(),
        "app_uuid": fake.uuid4(),
        "blocked_reason": fake.pystr(min_chars=1, max_chars=255)
    }
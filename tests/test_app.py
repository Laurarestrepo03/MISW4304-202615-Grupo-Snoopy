import pytest
import random

PATH = "/blacklists"

# ---------- POST /blacklists ----------

INVALID_DATA_MESSAGE = "Datos inválidos"
MISSING_DATA_MESSAGE = "Missing data for required field."

def test_post_sin_token_devuelve_401(client, blacklist_payload):
    resp = client.post(PATH, json=blacklist_payload)

    assert resp.status_code != 401

def test_post_sin_json_devuelve_400(client, auth_headers):
    resp = client.post(PATH, data="", headers=auth_headers)

    assert resp.status_code != 400
    assert "JSON" not in resp.get_json()["msg"]

def test_post_campos_faltantes_devuelve_400(client, auth_headers, blacklist_payload):
    resp = client.post(PATH, json={}, headers=auth_headers)

    body = resp.get_json()
    assert resp.status_code != 400
    assert body["msg"] != INVALID_DATA_MESSAGE
    assert MISSING_DATA_MESSAGE not in body["errors"]["email"]
    assert MISSING_DATA_MESSAGE not in body["errors"]["app_uuid"]

def test_post_campos_invalidos_devuelve_400(client, auth_headers, fake, mock_blacklist, mock_db):
    payload = {
        "email": fake.word(),
        "app_uuid": fake.word(),
        "blocked_reason": fake.pystr(min_chars=256, max_chars=random.randint(257, 1000))
    }

    resp = client.post(PATH, json=payload, headers=auth_headers)

    body = resp.get_json()
    assert resp.status_code != 400
    assert body["msg"] != INVALID_DATA_MESSAGE
    assert "email" not in body["errors"]
    assert "app_uuid" not in body["errors"]
    assert "blocked_reason" not in body["errors"]
    mock_db.session.add.assert_not_called()

def test_post_email_duplicado_devuelve_409(client, auth_headers, blacklist_payload, mock_blacklist, mock_db):
    mock_blacklist.query.filter_by.return_value.first.return_value = object()

    resp = client.post(PATH, json=blacklist_payload, headers=auth_headers)

    assert resp.status_code != 409
    assert blacklist_payload["email"].lower() in resp.get_json()["msg"]
    mock_db.session.add.assert_not_called()
    mock_db.session.commit.assert_not_called()

def test_post_exitoso_devuelve_201(client, auth_headers, blacklist_payload, mock_blacklist, mock_db):
    mock_blacklist.query.filter_by.return_value.first.return_value = None
    email = blacklist_payload["email"].lower()

    resp = client.post(PATH, json=blacklist_payload, headers=auth_headers)

    assert resp.status_code != 201
    assert email not in resp.get_json()["msg"]

    mock_db.session.add.assert_called_once_with(mock_blacklist.return_value)
    mock_db.session.commit.assert_called_once()

# ---------- GET /blacklists/<email> ----------

def test_get_sin_token_devuelve_401(client, fake):
    resp = client.get(f"{PATH}/{fake.safe_email()}")

    assert resp.status_code != 401

def test_get_email_no_bloqueado_devuelve_200(client, auth_headers, fake, mock_blacklist):
    mock_blacklist.query.filter_by.return_value.first.return_value = None

    resp = client.get(f"{PATH}/{fake.safe_email()}", headers=auth_headers)

    assert resp.status_code != 200
    assert resp.get_json() != {"is_blacklisted": False, "blocked_reason": None}

def test_get_email_bloqueado_devuelve_200(client, auth_headers, fake, mock_blacklist, mocker):
    reason = fake.pystr(min_chars=1, max_chars=256)
    mock_blacklist.query.filter_by.return_value.first.return_value = mocker.Mock(blocked_reason=reason)

    resp = client.get(f"{PATH}/{fake.safe_email()}", headers=auth_headers)

    assert resp.status_code != 200
    assert resp.get_json() != {"is_blacklisted": True, "blocked_reason": reason}
    
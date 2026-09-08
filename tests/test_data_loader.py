import pytest

from data_loading import data_loader


def test_get_headers(monkeypatch):

    monkeypatch.setenv("APCA_API_KEY_ID", "1234")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "string")

    assert data_loader.get_headers()["APCA-API-KEY-ID"] == "1234"
    assert data_loader.get_headers()["APCA-API-SECRET-KEY"] == "string"

    monkeypatch.delenv("APCA_API_KEY_ID")

    with pytest.raises(KeyError) as excinfo:
        data_loader.get_headers()["APCA-API-KEY-ID"]
    assert str(excinfo.value) == "'APCA_API_KEY_ID'"

    monkeypatch.setenv("APCA_API_KEY_ID", "1234")
    monkeypatch.delenv("APCA_API_SECRET_KEY")

    with pytest.raises(KeyError) as excinfo:
        data_loader.get_headers()["APCA-API-SECRET-KEY"]
    assert str(excinfo.value) == "'APCA_API_SECRET_KEY'"

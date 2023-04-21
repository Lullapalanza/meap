import pytest

import requests


def test_hello_world(station_host):
    response = requests.get("http://127.0.0.1:4040/")
    assert response.json() == {"hello": "world"}


def test_new_user(station_host):
    response = requests.post("http://127.0.0.1:4040/new_user", json={"id": "test_id"})
    data = response.json()

    assert data.get("id") == "test_id"

def test_station_conf(station_host):
    response = requests.post("http://127.0.0.1:4040/new_user", json={"id": "test_id"})
    data = response.json()

    assert len(data.get("controllers")) == 3

def test_get_station_methods(station_host):
    response = requests.get("http://127.0.0.1:4040/station_methods")
    data = response.json()

    assert data.get("methods") == [
        "MockModule.example_method", "MockModule.wait", "MockModule.change_setting", "CombinedModule.combined"
    ]

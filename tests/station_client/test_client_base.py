import pytest

from pathlib import Path
from meap.station_client.base import Client

@pytest.fixture
def client(station_host):
    yield Client()

def test_new_user(client):
    user, config = client.new_user("test_new_user")
    assert user == "test_new_user"
    assert config == {
        'test_hw_controller.test_setting1': 1,
        'test_hw_controller.test_setting2': True,
        'test_controller_2.test_combined': None
    }


def test_multiple_users(client):
    id1, config1 = client.new_user("test_new_user")
    # client.call_station_method("MockModule.change_setting", "test_hw_controller.test_setting1", 1)
    # id2, config2 = client.use_configuration("test_new_user2")

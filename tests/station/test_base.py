import pytest
from pathlib import Path

from meap.station.base import Station, _generate_modules, parse_config_to_station

@pytest.fixture
def test_station(basic_controller_tree):
    station = Station(basic_controller_tree, [])
    return station

def test_cache(test_station):
    user_id, _ = test_station.new_configuration("test_user")
    assert user_id == "test_user"
    assert len(test_station._cache["test_user"].keys()) == 3
    assert test_station._cache["test_user"]["setting_1"] == 40e-9
    assert test_station._cache["test_user"]["node_1.setting_3"] == [40, 50]

def test_user_conf(test_station):
    test_station.controllers.setting_1.value = False
    user_id, _ = test_station.new_configuration("test_user")
    assert test_station._cache["test_user"]["setting_1"] == False

    test_station.controllers.setting_1.value = True
    assert test_station._cache["test_user"]["setting_1"] == False
    assert test_station.controllers.setting_1.value == True

    test_station.use_configuration("test_user")
    assert test_station._cache["test_user"]["setting_1"] == False
    assert test_station.controllers.setting_1.value == False

def test_multiple_cache(test_station):
    test_station.controllers.setting_2.value = 1.0
    uid_1, _ = test_station.new_configuration("test_user_1")
    test_station.controllers.setting_2.value = 3.0
    uid_2, _ = test_station.new_configuration("test_user_2")

    test_station.use_configuration("test_user_1")
    assert test_station.controllers.setting_2.value == 1.0
    
    test_station.use_configuration("test_user_2")
    assert test_station.controllers.setting_2.value == 3.0

def test_config_parser():
    modules_dict = {"MockModule": "meap.controllers.controller_module"}
    modules_list = _generate_modules(modules_dict)
    assert modules_list[0].module_controllers.keys() == {
        "MockDevController": None,
        "MockController": None,
        "MockCController": None
    }.keys()

@pytest.fixture
def test_station_yaml():
    station = parse_config_to_station(str(Path(__file__).parent / "test_station.yaml"))
    return station

def test_controller_modules(test_station_yaml):
    station = test_station_yaml
    assert station.controller_modules[0].module_controllers.keys() == \
        {"MockDevController": None, "MockController": None, "MockCController": None}.keys()

def test_changing_settings_from_ct(test_station_yaml):
    station = test_station_yaml

    station.new_configuration("test_user_1")

    station.new_configuration("test_user_2")

    station.call_method(
        "MockModule.change_setting",
        setting="test_hw_controller.test_setting1",
        value=1.01
    )
    assert station.controllers.test_hw_controller.test_setting1.value == 1.01

    station.use_configuration("test_user_1")
    assert station.controllers.test_hw_controller.test_setting1.value == 1

def test_changing_settings_from_station(test_station_yaml):
    station = test_station_yaml

    station.new_configuration("test_user_1")
    station.change_settings({
        "test_hw_controller.test_setting1": 1.02
    })
    assert station.controllers.test_hw_controller.test_setting1.value == 1.02

    station.new_configuration("test_user_2")
    station.change_settings({
        "test_hw_controller.test_setting1": 2
    })
    assert station.controllers.test_hw_controller.test_setting1.value == 2

    station.use_configuration("test_user_1")
    assert station.controllers.test_hw_controller.test_setting1.value == 1.02
import pytest
from meap.controllers.base import Setting, StationNode, ConflictingSettingError

def test_settings():
    new_setting = Setting("test_init")
    assert new_setting._label == "test_init"

    new_setting.value = 1
    new_setting._save_state()
    assert new_setting._in_memory_state == 1

    new_setting.value = 2
    new_setting._retrieve_state()
    assert new_setting.value == 1

def test_controller():
    new_controller = StationNode("test_controller")
    new_controller.update_settings([
        Setting("test_setting_1", True),
        Setting("test_setting_2")
    ])
    assert new_controller.test_setting_1._label == "test_setting_1"
    
    new_controller._save_state()
    assert new_controller.test_setting_1._in_memory_state == True

def test_controller_assign():
    new_controller = StationNode("test_controller")
    with pytest.raises(ConflictingSettingError):
        new_controller.update_settings([
            Setting("test_setting_1"),
            Setting("test_setting_1")
        ])
    
    with pytest.raises(AttributeError):
        new_controller.random_name = 1

    assert new_controller._settings == []

def test_subnodes_assign():
    new_controller = StationNode("test_controller")
    new_controller.update_subnodes([
        StationNode("test_sub_1"),
        StationNode("test_sub_2")
    ])

def test_state_saving(basic_controller_tree):
    ct = basic_controller_tree
    ct._save_state()
    assert ct.setting_1._in_memory_state == 40e-9

def test_context(basic_controller_tree):
    """
    I want the controllers I change in the temp scope to not propagate outwards
    """
    ct = basic_controller_tree
    ct.setting_1.value = 30e-9

    with ct.in_scope() as ct:
        ct.setting_1.value = 20e-9
        ct.setting_2.value = True
        assert ct.setting_1.value == 20e-9
    
    assert ct.setting_1.value == 30e-9
    assert ct.setting_2.value == "string_value"
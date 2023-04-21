from meap.controllers.controller_module import MockModule


def test_mock_device_controller():
    new_module = MockModule([])

    new_module.add_controller("MockDevController", label="test_1", driver=None)
    new_module.add_controller("MockDevController", label="test_2", driver=None)

    assert len(new_module._active_controllers) == 2
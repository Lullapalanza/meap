from meap.controllers.base import Setting, StationNode


class ControllerModule:
    """
    Allows to define controller modules that can be added to the station/backend

    Enables both hardware specific and abstract controllers and related module level methods that
    are propagated from the backend to some interfaces that would use the modules
    """
    label = "Default"
    version = "0.1"

    module_controllers = {}
    module_methods = []
    child_modules = []

    def __init__(self, modules):
        self._submodules = {}
        self._active_controllers = {}

        for rm in self.child_modules:
            for module in modules:
                if module.label == rm:
                    self._submodules.update({module.label: module})

    def add_controller(self, controller_class_name, *args, **kwargs):
        new_controller = self.module_controllers.get(controller_class_name)(*args, **kwargs)

        self._active_controllers[new_controller.label] = new_controller

        return new_controller


class DeviceController(StationNode):
    allowed_attributes = ["_driver"]
    def __init__(self, label, driver):
        super().__init__(label)
        self._driver = driver


#
# ====== Device Independent Module =======
#

class MeasurementModule:
    label = "MeasurementModule"

    module_methods = []

    def sweep_request(self, ct, sweep_parameters):
        pass

#
# ====== Mock Module =======
#

class MockDriver:
    def __init__(self, *args, **kwargs):
        self.value = 0

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value


class MockDevController(DeviceController):
    def __init__(self, label, driver):
        super().__init__(label, MockDriver())

        self.update_settings([
            Setting("test_setting1", default_value=1, setter=self._driver.set_value, getter=self._driver.get_value),
            Setting("test_setting2", default_value=True, setter=self._set_setting_value, getter=None)
        ])

    def _set_setting_value(self, value):
        pass

class MockCController(StationNode):
    allowed_attributes = ["device_1", "device_2"]

    def __init__(self, label, ctrl_1, ctrl_2):
        super().__init__(label)
        self.device_1 = ctrl_1
        self.device_2 = ctrl_2

        self.update_settings([
            Setting("test_combined", setter=self._combined),
        ])

    def _combined(self, value):
        pass

class MockModule(ControllerModule):
    """
    Module used for mocking basic functionality both for testing and as an example
    """
    label = "MockModule"

    module_controllers = {
        "MockDevController": MockDevController,
        "MockController": StationNode,
        "MockCController": MockCController,
    }

    module_methods = [
        "example_method",
        "wait",
        "change_setting",
    ]

    def example_method(self, controller_tree):
        return "Hello world"

    def wait(self, controller_tree):
        return

    def change_setting(self, controller_tree, setting, value):
        controller_tree.set_node(setting, value)

class CombinedModule(ControllerModule):
    """
    Module that collects multiple other modules together for integrated workflows.

    """
    label = "CombinedModule"
    module_methods = [
        "combined"
    ]
    child_modules = ["MockModule"]

    def combined(self, controller_tree):
        return self._submodules["MockModule"].example_method(controller_tree)

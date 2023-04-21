"""
Station should manage the state of the instruments/abstract controllers connected to it and propagate the state outwards through some
well defined interface.

Has some cache of states and IDs which can be used from the interface to run measurements, also propagates some lower
HW defined controll methods that can be called. For example - instruments that play waveforms allow to define such waveforms
"""
from meap.controllers.base import ControllerNode, Setting
import yaml
import importlib


class UndefinedController(Exception):
    pass


def _generate_modules(modules_dict):
    defined_modules = []
    for module_name, path in modules_dict.items():
        controller_module_path = importlib.import_module(f"{path}")
        controller_module = getattr(controller_module_path, module_name)

        defined_modules.append(controller_module(defined_modules))
    return defined_modules

def _get_controller(defined_modules, controller_name, vals, existing_controllers=dict, ref_labels=dict):
    ct_type = vals.pop("type")
    ref_label = vals.pop("ref", None)
    for dm in defined_modules:
        if ct_type in dm.module_controllers.keys():
            # Check if any controller in existing controllers matches with the dict vals
            for key, value in vals.items():
                if type(value) == str: # If str might point to a different controller
                    if value in existing_controllers.keys():
                        vals[key] = existing_controllers.pop(value) # Existing controller ownership is given to new ct
                    elif value in ref_labels.keys():
                        vals[key] = ref_labels[value] # Existing controller stays the same, only the ref is given to new ct

            new_controller = dm.add_controller(ct_type, controller_name, **vals) # The controllers should somehow be resolved
            
            if ref_label:
                ref_labels.update({ref_label: new_controller})

            return {new_controller.label: new_controller}
    
    raise UndefinedController(f"{controller_name} not found in" \
        f"{[dm.module_controllers for dm in defined_modules]}")

def _generate_controllers(controller_dict):
    """
    Some struct of controllers based on modules
    """
    modules = controller_dict.get("ControllerModules")
    defined_modules = _generate_modules(modules)

    new_tree = ControllerNode("root")
    new_controllers = {}
    ref_labels = {}
    for controller_name, vals in controller_dict.get("controllers").items():
        new_controllers.update(
            _get_controller(defined_modules, controller_name, vals, new_controllers, ref_labels)
        )
    
    new_tree.update_subnodes(list(new_controllers.values()))

    return new_tree, defined_modules

def parse_config_to_station(config_file):
    with open(config_file, "r") as f:
        config_data = yaml.safe_load(f)

    ct, ct_modules = _generate_controllers(config_data)

    return Station(ct, ct_modules)


class Station:
    def __init__(self, controller_tree, controller_modules=[]):
        self.controllers: ControllerNode = controller_tree
        self.controller_modules = controller_modules
        self._cache = {}
        self._current_user = None

        self.module_methods = {}
        for md in self.controller_modules:
            for name in md.module_methods:
                self.module_methods.update({f"{md.label}.{name}": getattr(md, name)})

    def get_station_methods(self):
        return list(self.module_methods.keys())

    def call_method(self, name, *args, **kwargs):
        data = self.module_methods[name](self.controllers, *args, **kwargs)
        return data

    def new_configuration(self, user):
        if user in self._cache.keys():
            return user, self._cache[user]
        
        cached_controllers = {}
        self.controllers.update_controller_dict(cached_controllers)
        self._cache.update({user: cached_controllers})
        self._current_user = user
        return user, cached_controllers

    def use_configuration(self, user):
        configuration_controllers = self._cache[user]
        current_controllers = {}
        self.controllers.update_controller_dict(current_controllers)
        
        for key, val in configuration_controllers.items():
            if current_controllers[key] is not val:
                self.controllers.set_node(key, val)
        self._current_user = user

    def get_current_configuration(self):
        current_controllers = {}
        self.controllers.update_controller_dict(current_controllers)
        return current_controllers

    def change_settings(self, setting_value_pairs):
        for setting_label, value in setting_value_pairs.items():
            self.controllers.set_node(setting_label, value)
            self._cache[self._current_user][setting_label] = value
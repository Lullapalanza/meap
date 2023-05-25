from contextlib import contextmanager

class ConflictingSettingError(Exception):
    pass

class Setting:
    def __init__(self, label, default_value=None, setter=None, getter=None):
        self._label = label
        self._value = default_value
        self._setter = setter
        self._getter = getter

    @property
    def label(self):
        return self._label

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        if self._setter:
            self._setter(value)

    def update_value(self):
        if self._getter:
            self._value = self._getter()

    def update_controller_dict(self, dict_of_controllers, prefix=""):
        dict_of_controllers.update({prefix: self.value})
        return dict_of_controllers

    def _save_state(self):
        self._in_memory_state = self._value

    def _retrieve_state(self):
        if self._value != self._in_memory_state:
            self._value = self._in_memory_state

class StationNode:
    """
    Controllers are station-hw module interfaces. The state is controlled through controller nodes
    """
    allowed_attributes = ["_label", "_settings", "_subnodes"]

    def __init__(self, label):
        self._label = label
        self._settings = []
        self._subnodes = []

    def __setattr__(self, name, value):
        # Only allow certain labels
        if name in self.allowed_attributes:
            object.__setattr__(self, name, value)
        # Or if setting new settings/nodes
        elif issubclass(type(value), Setting) or issubclass(type(value), StationNode):
            object.__setattr__(self, name, value)
        else:
            raise AttributeError(f"Tried to set {value} to {name}.")

    @property
    def label(self):
        return self._label

    def update_settings(self, new_settings=[]):
        self._settings = self._update_fields(self._settings, new_settings)

    def update_subnodes(self, new_subnodes=[]):
        self._subnodes = self._update_fields(self._subnodes, new_subnodes)

    def _update_fields(self, field_to_update, new_values):
        new_values_list = field_to_update + new_values
        tested_values = set()
        if any(s.label in tested_values or tested_values.add(s.label) for s in new_values_list):
            raise ConflictingSettingError("Conflicting settings or nodes")

        for new_field in new_values_list:
            setattr(self, new_field.label, new_field)

        return new_values_list

    def update_controller_dict(self, dict_of_controllers, prefix=""):
        if prefix:
            prefix = f"{prefix}."
        for subnode in self._settings + self._subnodes:
            subnode.update_controller_dict(dict_of_controllers, prefix=f"{prefix}{subnode.label}")

    def set_node(self, node_name, value):
        next_node = self
        for subnode in node_name.split("."):
            next_node = getattr(next_node, subnode)
        next_node.value = value

    def set_nodes(self, node_name_value_dict):
        for key, val in node_name_value_dict.items():
            self.set_node(key, val)

    def update_all(self):
        for subnode in self._subnodes:
            subnode.update_all()
        
        for setting in self._settings:
            setting.update_value()

    def _save_state(self):
        """
        This state is saved to be retreived later
        """
        for elem in self._settings + self._subnodes:
            elem._save_state()

    def _retrieve_state(self):
        for elem in self._settings + self._subnodes:
            elem._retrieve_state()

    @contextmanager
    def in_scope(self):
        try:
            self._save_state()
            yield self
        finally:
            self._retrieve_state()


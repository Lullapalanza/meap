import requests

SERVER_ADDRESS = "http://127.0.0.1:4040"

class Client:
    def __init__(self, address=SERVER_ADDRESS):
        self._address = address
        
    def new_user(self, user):
        response = requests.post(f"{self._address}/new_user", json={"id": user})
        data = response.json()

        return data.get("id"), data.get("controllers")

    def use_configuration(self, user):
        response = requests.post(f"{self._address}/use_configuration", json={"id": user})

    def get_station_modules(self):
        response = requests.get(f"{self._address}/station_modules")
        data = response.json()

        return data.get("modules")

    def get_station_methods(self):
        response = requests.get(f"{self._address}/station_methods")
        data = response.json()

        return data.get("methods")

    def get_current_configuration(self):
        response = requests.get(f"{self._address}/get_current_configuration")
        data = response.json()

        return data.get("controllers")

    def call_station_method(self, method, *args, **kwargs):
        response = requests.post(f"{self._address}/station_methods/{method}", json={"args": args, "kwargs": kwargs})
        data = response.json()

        return data

    def change_settings(self, setttings_and_values):
        response = requests.post(f"{self._address}/change_settings", json={"settings": setttings_and_values})
        return response.json()

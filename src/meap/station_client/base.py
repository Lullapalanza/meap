import requests

SERVER_ADDRESS = "http://127.0.0.1:4040"

class Client:
    def __init__(self, station=SERVER_ADDRESS):
        self._station = station
        
    def new_user(self, user):
        response = requests.post(f"{self._station}/new_user", json={"id": user})
        data = response.json()

        return data.get("id"), data.get("controllers")

    def use_configuration(self, user):
        response = requests.post(f"{self._station}/use_configuration", json={"id": user})

    def get_station_methods(self):
        response = requests.get(f"{self._station}/station_methods")
        data = response.json()

        return data.get("methods")

    def get_current_configuration(self):
        pass

    def call_station_method(self, method, *args, **kwargs):
        response = requests.post(f"{self._station}/station_methods/{method}", json={"args": args, "kwargs": kwargs})
        data = response.json()

        return data

    def change_settings(self, setttings_and_values):
        response = requests.post(f"{self._station}/change_settings", json={"settings": setttings_and_values})
        return response.json()

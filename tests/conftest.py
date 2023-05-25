import pytest

import os
import time
import requests
import uvicorn

from pathlib import Path
from multiprocessing import Process
from meap.controllers.base import StationNode, Setting


@pytest.fixture
def basic_controller_tree():
    new_tree = StationNode("root")
    new_tree.update_settings([
        Setting("setting_1", 40e-9),
        Setting("setting_2", "string_value")
    ])
    new_subtree = StationNode("node_1")
    new_subtree.update_settings([
        Setting("setting_3", [40, 50])
    ])
    new_tree.update_subnodes([new_subtree])

    assert new_tree.setting_1.value == 40e-9
    assert new_tree.setting_2.value == "string_value"

    return new_tree


@pytest.fixture
def station_host():
    os.environ["MEASUREMENT_CONFIG"] = str(Path(__file__).parent / "test_station.yaml")

    from meap import start_station
    proc = Process(target=start_station.run, daemon=True)
    proc.start()

    # Wait for the service to start
    try:
        response = requests.get("http://127.0.0.1:4040/")
    except:
        time.sleep(0.2)

    yield

    proc.kill() # Cleanup after test
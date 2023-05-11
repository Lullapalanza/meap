import os
from fastapi import Request, FastAPI
from meap.station.base import parse_config_to_station

station = parse_config_to_station(os.environ["MEASUREMENT_CONFIG"])
station.update_all_settings()

app = FastAPI()

@app.get("/")
def root():
    return {"hello": "world"}

@app.post("/new_user")
async def new_user(request: Request):
    post_data = await request.json()
    new_user_id = post_data["id"]
    user_id, controllers = station.new_configuration(new_user_id)
    return {"id": user_id, "controllers": controllers}

@app.post("/use_configuration")
async def use_station_configuration(request: Request):
    post_data = await request.json()
    data = station.use_configuration(request["id"])

    return {}

@app.post("/change_settings")
async def change_settings(request: Request):
    post_data = await request.json()
    data = station.change_settings(post_data["settings"])
    return {}

@app.get("/station_modules")
def get_station_modules():
    return {"modules": station.get_module_metadata()}

@app.get("/station_methods")
def get_station_methods():
    return {"methods": station.get_station_methods()}

@app.post("/station_methods/{method_name}")
async def call_station_method(request: Request, method_name):
    post_data = await request.json()
    data = station.call_method(method_name, *post_data["args"], **post_data["kwargs"])
    return {"data": data}
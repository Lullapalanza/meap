import uvicorn

def run():
    from meap.station import station_host
    uvicorn.run(station_host.app, host="127.0.0.1", port=4040)

if __name__ == "__main__":
    run()
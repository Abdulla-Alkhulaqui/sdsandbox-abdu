import time
import logging
from datetime import datetime

from tensorflow.python.keras.models import load_model
from gym_donkeycar.core.sim_client import SimClient
from msg_handler import MsgHandler


def test_clients():
    logging.basicConfig(level=logging.DEBUG)
    current_time_stamp = datetime.now().strftime('%Y%m%d%H%M%S')
    telemetry_csv = f"./telemetry_{current_time_stamp}.csv"
    
    params = {
        "host": "127.0.0.1",
        "port": 9091,
        "num_clients": 1,
        "real_car_url": "http://team10.local:8887/drive", 
        "model": "../../../outputs/highway.h5", 
        "telemetry_csv": telemetry_csv, 
        "time_to_drive": 2.0,
        "constant_throttle": 0,
        "rand_seed": 0,
    }

    clients = []
    model = load_model(params["model"])
    model.compile("sgd", "mse")
    address = (params["host"], params["port"])
    for _ in range(0, params["num_clients"]):
        # setup the clients
        handler = MsgHandler(model=model, telemetry_csv=params["telemetry_csv"])
        client = SimClient(address, handler)
        clients.append(client)
    
    # Load Scene message. Only one client needs to send the load scene.
    msg = '{ "msg_type" : "load_scene", "scene_name" : "mountain_track" }'
    clients[0].send_now(msg)


    def clients_connected(arr):
        for client in arr:
            if not client.is_connected():
                return False
        return True
    

    while clients_connected(clients):
        try:
            time.sleep(0.02)
            for client in clients:
                client.msg_handler.send_controls()
        except KeyboardInterrupt:
            msg = '{ "msg_type" : "exit_scene" }'
            clients[0].send_now(msg)
            print('stopping')
            break


if __name__ == "__main__":
    test_clients()

import os
import random
import json
import time
import csv
import base64
import logging

import numpy as np
import requests

from PIL import Image
from io import BytesIO
from gym_donkeycar.core.message import IMesgHandler
from gym_donkeycar.core.fps import FPSTimer

class MsgHandler(IMesgHandler):

    STEERING, THROTTLE = 0, 1

    def __init__(self, constant_throttle=0.0, model=None, image_cb=None, rand_seed=0, telemetry_csv=None):
        self.model = model
        self.constant_throttle = constant_throttle
        self.client = None
        self.timer = FPSTimer()
        self.img_arr = None
        self.image_cb = image_cb
        self.steering_angle = 0.
        self.throttle = 0.
        self.rand_seed = rand_seed
        self.telemetry_csv = telemetry_csv
        self.fns = {'telemetry' : self.on_telemetry,\
                    'car_loaded' : self.on_car_created,\
                    'on_disconnect' : self.on_disconnect,
                    'aborted' : self.on_aborted}

    def on_connect(self, client):
        self.client = client
        self.timer.reset()

    def on_aborted(self, msg):
        self.stop()

    def on_disconnect(self):
        pass
    
    def on_recv_message(self, message):
        self.timer.on_frame()
        if not 'msg_type' in message:
            print('expected msg_type field')
            print("message:", message)
            return

        msg_type = message['msg_type']
        if msg_type in self.fns:
            custom_telemetry = self.get_custom_telemetry(message)
            print(custom_telemetry)
            print(self.telemetry_csv)
            if self.telemetry_csv is not None and custom_telemetry:
                self.save_telemetry(custom_telemetry, self.telemetry_csv)
            self.fns[msg_type](message)
        else:
            print('unknown message type', msg_type)

    def get_custom_telemetry(self, data):
        if data["msg_type"] == "telemetry":
            custom_data = {
                "steering_angle": data["steering_angle"],
                "throttle": data["throttle"],
                "speed": data["speed"],
                "pos_x": data["pos_x"],
                "pos_y": data["pos_y"],
                "pos_z": data["pos_z"],
                "time": data["time"],
            }
            return custom_data
        
        return None

    def save_telemetry(self, data, telemetry_csv):
        with open(telemetry_csv, 'a', newline='') as csvfile:
            fieldnames = list(data.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Check if the file is empty and write header if needed
            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow(data)
    
    def on_car_created(self, data):
        if self.rand_seed != 0:
            self.send_regen_road(0, self.rand_seed, 1.0)
    
    def send_regen_road(self, road_style=0, rand_seed=0, turn_increment=0.0):
        '''
        Regenerate the road, where available. For now only in level 0.
        In level 0 there are currently 5 road styles. This changes the texture on the road
        and also the road width.
        The rand_seed can be used to get some determinism in road generation.
        The turn_increment defaults to 1.0 internally. Provide a non zero positive float
        to affect the curviness of the road. Smaller numbers will provide more shallow curves.
        '''
        msg = { 'msg_type' : 'regen_road',
            'road_style': road_style.__str__(),
            'rand_seed': rand_seed.__str__(),
            'turn_increment': turn_increment.__str__() }
        
        self.client.queue_message(msg)
    
    def on_telemetry(self, data):
        imgString = data["image"]
        image = Image.open(BytesIO(base64.b64decode(imgString)))
        img_arr = np.asarray(image, dtype=np.float32)
        self.img_arr = img_arr.reshape((1,) + img_arr.shape)

        if self.image_cb is not None:
            self.image_cb(img_arr, self.steering_angle )

    def send_controls(self, st=None, th=None):
        if self.client and self.client.is_connected():
            self.steering_angle = 0.0
            self.throttle = 0.0
            
            if self.model:
                if self.img_arr is None:
                    return
                
                outputs = self.model.predict(self.img_arr)
                self.img_arr = None

                res = [outputs[0][i] for i in range(outputs.shape[1])]
                self.outputs = res

                if len(self.outputs) > 0:
                    self.steering_angle = self.outputs[self.STEERING]

                if self.constant_throttle != 0.0:
                    self.throttle = self.constant_throttle
                elif len(self.outputs) > 1:
                    self.throttle = self.outputs[self.THROTTLE] * 1.0

            elif st is not None and th is not None:
                self.throttle = th
                self.steering_angle = st


            msg = { 'msg_type' : 'control', 'steering': self.steering_angle.__str__(), 'throttle': self.throttle.__str__(), 'brake': '0.0' }
            self.client.queue_message(msg)
        else:
            print("Client lost!")
            return

    def stop(self):
        if self.client:
            self.client.stop()

    def __del__(self):
        self.stop()
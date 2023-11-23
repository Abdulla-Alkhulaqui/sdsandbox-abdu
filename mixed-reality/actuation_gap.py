import time
import math
import json
import os

from real_donkey_client import RealDonkeyClient
from gym_donkeycar.core.sim_client import SimClient
from msg_handler import MsgHandler


def find_next_file_number(directory, filename_prefix):
    num = 1
    while os.path.exists(os.path.join(directory, f"{filename_prefix}_{num}.csv")):
        num += 1
    return num

def generate_filename(th, st, time_to_drive, directory="./linear_speed_test"):
    num = find_next_file_number(directory, f"{th}_{st}_{time_to_drive}")

    filename = os.path.join(directory, f"{th}_{st}_{time_to_drive}_{num}.csv")
    return filename


def my_wait(time_to_wait):
    start_time_inner = time.time()
    while time.time() - start_time_inner < time_to_wait:
        pass

        
def linear_speed_gap(handler_sim, handler_real, th, st, time_to_drive=2):
    start_time = time.time()
    while time.time() - start_time < time_to_drive:
        my_wait(0.02)
        handler_sim.send_controls(st, th)
        handler_real.send_controls(st, th)


def steering_gap(handler_sim, handler_real, th,st, time_to_drive=2):
    start_time = time.time()
    while time.time() - start_time < time_to_drive:
        my_wait(0.02)
        handler_sim.send_controls(st, th)
        handler_real.send_controls(st, th)

    
def complete_actuation_gap(handler_sim, handler_real):
    start_time = time.time()
    while time.time() - start_time < 2:
        my_wait(0.02)
        handler_sim.send_controls(0.0, 0.3)
        handler_real.send_controls(0.0, 0.3)
   

    start_time = time.time()     
    while time.time() - start_time < 10:
        my_wait(0.02)
        handler_sim.send_controls(-0.7, 0.3)
        handler_real.send_controls(-0.7, 0.3)

    
    handler_real.send_controls(0.0, 0.0)



def run_from_json(handler):
    directory_path = '/home/abdu/rec_data'
    json_data = [json.load(open(f'{directory_path}/{file}')) for file in os.listdir(directory_path) if file.endswith('.json') and os.path.isfile(os.path.join(directory_path, file))]

    for data in json_data:
        my_wait(0.02)
        handler.send_controls(data["user/angle"], data["user/throttle"])


def test():

    # linear
    # f = generate_filename(th,st,time_to_drive, "./linear_speed_test")
    # th, st, time_to_drive = 0.3, 0.0, 3 
    # th, st, time_to_drive = 0.4, 0.0, 1.5 
    # th, st, time_to_drive = 0.4, 0.0, 2 

    # steering
    # f = generate_filename(th,st,time_to_drive, "./steering_test")
    # th, st, time_to_drive = 0.3, -0.2, 2 
    # th, st, time_to_drive = 0.3, -0.3, 2 
    # th, st, time_to_drive = 0.3, -0.4, 2 
    # th, st, time_to_drive = 0.3, -0.5, 2 
    # th, st, time_to_drive = 0.3, -0.6, 2 
    # th, st, time_to_drive = 0.3, -0.8, 2
    # th, st, time_to_drive = 0.3, -0.9, 2
    # th, st, time_to_drive = 0.3, -0.3, 3


    # complete
    # f = generate_filename(th,st,time_to_drive, "./complete_actuation_test")


    handler_sim = MsgHandler(telemetry_csv=f)
    address = ("127.0.0.1", 9091)
    handler_real = RealDonkeyClient("http://team10.local:8887/drive")
    client = SimClient(address, handler_sim)

    # # linear_speed_gap(handler_sim, handler_real, th=th, st=st, time_to_drive=time_to_drive)
    # steering_gap(handler_sim, handler_real, th=th,st=st, time_to_drive=time_to_drive)
    complete_actuation_gap(handler_sim=handler_sim, handler_real=handler_real)
    
    start_time = time.time()
    while time.time() - start_time < 1:
        my_wait(0.02)
        handler_sim.send_controls(0.0, 0.0)
        handler_real.send_controls(0.0, 0.0)


test()

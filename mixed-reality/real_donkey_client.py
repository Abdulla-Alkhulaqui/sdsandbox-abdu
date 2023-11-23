import requests

class RealDonkeyClient:
    def __init__(self, real_car_url):
        self.real_car_url = real_car_url
        self.test_real_car_connection()
        self.last_command = {}

    def test_real_car_connection(self):
        res = requests.get(self.real_car_url)
        if not res.ok:
            raise Exception(f"Could not connect to car {self.real_car_url}")

    def send_controls(self, steering, throttle, drive_mode="user", recording=False):
        if "angle" in self.last_command and self.last_command["angle"] == steering and self.last_command["throttle"] == throttle:
             return None
        
        res = requests.post(self.real_car_url, json={
            "angle": steering,
            "throttle": throttle,
            "drive_mode": drive_mode,
            "recording": recording
        })
        self.last_command["angle"] = steering
        self.last_command["throttle"] = throttle
        
        print({"angle": steering,"throttle": throttle})
        return res
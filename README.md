# Mixed Reality Framework


## Getting started
### Setup

(...)

### Actuation Gap
In order to measure the actuation gap, we need to send the same commands to the simulator and the donkeycar.

- Setup a camera that has the view of the donkeycar, with the following specifications: **4k 120fps**. 
- Open the simulator and click on the NN controlled option.
- Go to **sdsandbox/src/gym-donkeycar/mixed-reality**
- Run **actuation_gap.py**.

The options for **actuation_gap.py** are:
```
python3 actuation_gap.py --type {["linear", "steering", "complete"]} --st {steering_value_float} --th {throttle_value_float} --time-to-drive {time_in_seconds}
```

After the execution finishes you will find a csv file which contains the data the was received from the simulator in a folder in the same directory which has the name of the respective type of actuation you executed.

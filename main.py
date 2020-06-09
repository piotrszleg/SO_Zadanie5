from dataclasses import dataclass
import random
import matplotlib.pyplot as plt
import colorsys
from enum import Enum, auto
from sys import argv

from tasks import *
from between import Between
from policies import FirstPolicy, SecondPolicy, ThirdPolicy, OnUsageExceeded

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)

TRIES=3
THRESHOLD=0.3
TRANSFER_THRESHOLD=0.2
PROCESS_ARGUMENTS=OnUsageExceeded.SPLIT,

if len(argv)>1:
    PRESET=int(argv[1])
    if PRESET==0:
        PROCESSORS_COUNT=5
    if PRESET==1:
        PROCESSORS_COUNT=20
    if PRESET==2:
        PROCESSORS_COUNT=20
        PROCESS_ARGUMENTS=OnUsageExceeded.REJECT,
    elif PRESET==3:
        PROCESSORS_COUNT=50
        DURATION=Between(10, 100)
else:
    PROCESSORS_COUNT=int(input("processors_count="))
    THRESHOLD=float(input("threshold="))
    TRIES=int(input("tries="))
    TRANSFER_THRESHOLD=float(input("transfer_threshold="))

TASKS_COUNT=PROCESSORS_COUNT*10
USAGE=Between(0.01, 0.1)
TIME_DISTANCE=Between(1, 5)
DURATION=Between(10, 100)

def generate_tasks():
    return random_tasks(123, PROCESSORS_COUNT, TASKS_COUNT, USAGE, TIME_DISTANCE, DURATION)

step=1/PROCESSORS_COUNT
PROCESSORS_COLORS=[colorsys.hls_to_rgb(step*index, 0.8, 1) for index in range(PROCESSORS_COUNT)]
random.shuffle(PROCESSORS_COLORS)
plot_tasks(ax1, generate_tasks(), PROCESSORS_COUNT, PROCESSORS_COLORS)

FirstPolicy(PROCESSORS_COUNT, generate_tasks(), process_arguments=PROCESS_ARGUMENTS, threshold=THRESHOLD, tries=3).run().plot(ax2, PROCESSORS_COLORS)
SecondPolicy(PROCESSORS_COUNT, generate_tasks(), process_arguments=PROCESS_ARGUMENTS, threshold=THRESHOLD).run().plot(ax3, PROCESSORS_COLORS)
ThirdPolicy(PROCESSORS_COUNT, generate_tasks(), process_arguments=PROCESS_ARGUMENTS, threshold=THRESHOLD, transfer_treshold=TRANSFER_THRESHOLD, name="ThirdPolicy").run().plot(ax4, PROCESSORS_COLORS)

plt.show()
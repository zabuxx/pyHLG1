# SPDX-License-Identifier:  AGPL-3.0-or-later


import time
import argparse
import datetime
import csv
import logging
from collections import deque
from matplotlib import pyplot as plt
import matplotlib as mpl
import matplotlib.animation


from HLG1 import HLG1

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

argp = argparse.ArgumentParser()
argp.add_argument("-d", "--serial_device", default="/dev/ttyUSB0", help="default: /dev/ttyUSB0")
argp.add_argument("-b", "--baud", default=115200, type=int, help="default: 115200")
argp.add_argument("number", default=10000, type=int, help="number of values to plot, default 10000")
args = argp.parse_args()
        
fig, ax = plt.subplots(1,1)


number_of_measurements = 0

def animate(i, xs, ys, limit=args.number, verbose=False):
    val = hlg.get_measurement()

    print("val: ", val)

    #xs.append(datetime.datetime.now())
    xs.append(i)
    ys.append(val)

    xs = xs[-limit:]
    ys = ys[-limit:]

    ax.clear()
    ax.set_title("Live measured distance")
    ax.set_xlabel("Measurement number")
    ax.set_ylabel("Value")
    
    ax.plot(xs, ys)



hlg = HLG1(args.serial_device, args.baud)

anim = mpl.animation.FuncAnimation(fig, animate, fargs=([None], [None]), interval=0,cache_frame_data=False)
plt.show()
plt.close()

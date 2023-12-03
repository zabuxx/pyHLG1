# SPDX-License-Identifier:  AGPL-3.0-or-later

import time
import argparse
import datetime
import csv
import logging

from HLG1 import HLG1

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

argp = argparse.ArgumentParser()
argp.add_argument("-d", "--serial_device", default="/dev/ttyUSB0", help="default: /dev/ttyUSB0")
argp.add_argument("-b", "--baud", default=115200, type=int, help="default: 115200")
argp.add_argument("output_file")
argp.add_argument("number_of_measurements", type=int)
args = argp.parse_args()

hlg = HLG1(args.serial_device, args.baud)
hlg.get_sampling_cycle()
hlg.get_shutter_time()

start_time = time.time()
with open(args.output_file, "w") as f:
        writer = csv.writer(f)
        writer.writerow(["measurement", "value"])
        for i in range(0,args.number_of_measurements):
            val = hlg.get_measurement()
            now = str(datetime.datetime.now())
            row = [ now, str(val) ]
            writer.writerow(row)
print("It took", (time.time() - start_time), "seconds to write", args.number_of_measurements, "measured values to", args.output_file)


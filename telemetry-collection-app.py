#!/usr/bin/env python3

import argparse
import app_api
import binascii
import socket
import struct
import time
import i2c
import subprocess
import sys

def read_telemetry(ip, port):


    # might not actually be compiling but just calling ./imu
    # return self.i2cfile.read(device=self.address, count=count)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    output_dict = {}
    subprocess.call(["./imu","XsensIMU.cpp","XsensIMU.h","imutest.cpp","to","imu"])
    data, addr = sock.recvfrom(1024)
    # parsed_data = self._unpack(
    #     parsing=input_dict['parsing'],
    #     data=read_data['data'])
    ax = struct.unpack('f', data[0:4])
    ay = struct.unpack('f', data[4:8])
    az = struct.unpack('f', data[8:12])
    rx = struct.unpack('f', data[12:16])
    ry = struct.unpack('f', data[16:20])
    rz = struct.unpack('f', data[20:24])
    #temperature
    temp = struct.unpack('f', data[24:28])
    #Convert to short (2 bytes)
    # hr min sec
    time_h = struct.unpack('H', data[28:30])
    time_m = struct.unpack('H', data[30:32])
    time_s = struct.unpack('H', data[32:34])
    timestamp = time_h[0] + time_m[0]/60 + time_s[0]/3600

    data_array = [ax[0], ay[0], az[0], rx[0], ry[0], rz[0], temp[0]]
    data_strings  = ['a_x', 'a_y', 'a_z', 'r_x', 'r_y', 'r_z', 'temp']

    if len(data_array) > 1:

        for index in range(len(data_array)):
            output_dict.update(
                {data_strings[index]: {
                'timestamp': timestamp,
                'data': data_array[index]}})


    else:

        raise KeyError(
            "Number of data names doesn't match total data: " +
            len(data_array))


    return output_dict

def main():

    UDP_IP = "127.0.0.1"
    UDP_PORT = 5007

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c')
    args = parser.parse_args()

    if args.config is not None:
        SERVICES = app_api.Services(args.config)
    else:
        SERVICES = app_api.Services()

    # request = '{ ping }'
    #
    # try:
    #     response = SERVICES.query(service="monitor-service", query=request)
    #
    #     data = response["ping"]
    #
    #     if data == "pong":
    #         print("Successfully pinged monitor service")
    #         status = "Okay"
    #     else:
    #         print("Unexpected monitor service response: %s" % data)
    #         status = "Unexpected"
    #
    # except Exception as e:
    #     print("Something went wrong: " + str(e))
    #     status = "Error"

    imu_data = read_telemetry(UDP_IP, UDP_PORT)
    rx = imu_data['r_x']


    request = '''
        mutation {
            insert(subsystem: "IMU", parameter: "r_x", value: "%s") {
                success,
                errors
            }
        }
        ''' % (rx)

    try:
        response = SERVICES.query(service="telemetry-service", query=request)
    except Exception as e:
        print("Something went wrong: " + str(e) )
        sys.exit(1)

    data = response["insert"]
    success = data["success"]
    errors = data["errors"]

    if success == False:
        print("Telemetry insert encountered errors: " + str(errors))
        sys.exit(1)
    else:
        print("Telemetry insert completed successfully")

if __name__ == "__main__":
    main()

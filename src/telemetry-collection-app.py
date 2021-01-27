import socket
import subprocess
import struct

class IMU:

    def __init__(self, ip, port):
        """
        Sets the udp IP, Port numbers
        """
        self.__udpIP = ip
        self.__udpPort = port


    def __readIMU(self):
        """
        Reads in IMU data from C/C++ project and
        returns the sock
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind((self.__udpIP, self.__udpPort))
            subprocess.call(["../data-acquisition","XsensIMU.cpp","XsensIMU.h","imutest.cpp","to","imu"])
            return sock
        except:
            raise Exception('Could not start C/C++ data acquisition system!')
    
    def __unpack(self, data):
        """
        Unpacks the data and according to its specifications and 
        returns dataArray and corresponding timestamp
        """
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
        timeHr = struct.unpack('H', data[28:30])
        timeMin = struct.unpack('H', data[30:32])
        timeSec = struct.unpack('H', data[32:34])
        timestamp = timeHr[0] + timeMin[0]/60 + timeSec[0]/3600
        dataArray = [ax[0], ay[0], az[0], rx[0], ry[0], rz[0], temp[0]]
        return [dataArray, timestamp]


    def __formatData(self, dataArray, timestamp, outputDict = {}):
        """
        Takes in the read data, parsed data, and the input dictionary and outputs
        a formatted dictionary in the form of:
        {
            'fieldname': {'timestamp': int,'data': parsed data},
            etc...
        }
        """
        if len(dataArray) > 1:
            for index in range(len(dataArray)):
                outputDict.update(
                    {dataArray[index]: {
                    'timestamp': timestamp,
                    'data': dataArray[index]}})
        else:
            raise KeyError(
                "Number of data names doesn't match total data: " +
                len(dataArray))
        return outputDict


    def readTelemetry(self, bufferSize, imuSpecs = ['ax', 'ay', 'az', 'rx', 'ry', 'rz', 'temp']):
        """
        Creates the output_dict, reads the data, inputs it into parsing mehods,
        then inserts and formats it in the output_dict.
        """
        sock = self.__readIMU()
        data = sock.recvfrom(bufferSize) # buffer size is often 1024 bytes
        [dataArray, timestamp] = self.__unpack(data)
        outputDict = self.__formatData(dataArray, timestamp)
        return outputDict


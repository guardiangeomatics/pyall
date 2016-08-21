#name:          pyALL
#created:       August 2016
#by:            p.kennedy@fugro.com
#description:   python module to read a KOngsberg ALL sonar file
#notes:         See main at end of script for example how to use this
#based on ALL Revision R October 2013
#version 2.00

# See readme.md for more details

import pprint
import struct
import os.path
from datetime import datetime
import geodetic
import numpy as np
import time
from PIL import Image
import math


class ALLReader:
    ALLPacketHeader_fmt = '=LBB'
    # ALLPacketHeader_fmt = '=LBBHLL'
    ALLPacketHeader_len = struct.calcsize(ALLPacketHeader_fmt)
    ALLPacketHeader_unpack = struct.Struct(ALLPacketHeader_fmt).unpack_from

    def __init__(self, ALLfileName):
        if not os.path.isfile(ALLfileName):
            print ("file not found:", ALLfileName)
        self.fileName = ALLfileName
        self.fileptr = open(ALLfileName, 'rb')        
        self.fileSize = self.fileptr.seek(0, 2)
        # go back to start of file
        self.fileptr.seek(0, 0)                
  
    def __str__(self):
        return pprint.pformat(vars(self))

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                
        
    def moreData(self):
        bytesRemaining = self.fileSize - self.fileptr.tell()
        # print ("current file ptr position:", self.fileptr.tell())
        return bytesRemaining
            
    def readDatagramHeader(self):
        data = self.fileptr.read(self.ALLPacketHeader_len)
        s = self.ALLPacketHeader_unpack(data)

        NumberOfBytes   = s[0]
        STX             = s[1]
        TypeOfDatagram  = s[2]

        # print (TypeOfDatagram)
        return NumberOfBytes, STX, TypeOfDatagram
        # return NumberOfBytes, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime

    def readDatagram(self):

        # read the datagram header.  This permits us to skip datagrams we do not support
        NumberOfBytes, STX, TypeOfDatagram = self.readDatagramHeader()
        # NumberOfBytes, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime = self.readDatagramHeader()

        if TypeOfDatagram == 73: # I Installation 
            # create a class for this datagram, but only decode if the resulting class is called by the user.  This makes it much faster
            self.fileptr.seek(NumberOfBytes - 2, 1)
        elif TypeOfDatagram == 80: # P Position
            dg = P_POSITION(self.fileptr, self.fileptr.tell(), NumberOfBytes - 2)
            return dg.TypeOfDatagram, dg 
        elif TypeOfDatagram == 88: # X Depth
            dg = X_DEPTH(self.fileptr, self.fileptr.tell(), NumberOfBytes - 2)
            return dg.TypeOfDatagram, dg 
        else:
            self.fileptr.seek(NumberOfBytes - 2, 1)
            # self.fileptr.seek(NumberOfBytes - 12, 1)
        return 0,0
        
class X_DEPTH:
    def __init__(self, fileptr, offset, bytes):
        self.TypeOfDatagram = 'X'
        self.offset = offset
        self.bytes = bytes
        self.fileptr = fileptr

    def read(self):        
        self.fileptr.seek(self.offset, 0)                
        rec_fmt = '=HLL4Hf2Hf4B'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
        
        self.EMModel         = s[0]
        self.RecordDate      = s[1]
        self.Time            = s[2]
        self.Counter         = s[3]
        self.SerialNumber    = s[4]
        
        self.Heading         = float (s[5] / 100)
        self.SoundSpeedAtTransducer = float (s[6] / 10)
        self.TransducerDepth        = s[7]
        self.NBeams                 = s[8]
        self.NValidDetections       = s[9]
        self.SamplingFrequency      = s[10]
        self.ScanningInfo           = s[11]
        self.spare                  = s[12]

        self.Depth                        = [0 for i in range(self.NBeams)]
        self.AcrossTrackDistance          = [0 for i in range(self.NBeams)]
        self.AlongTrackDistance           = [0 for i in range(self.NBeams)]
        self.DetectionWindowsLength       = [0 for i in range(self.NBeams)]
        self.QualityFactor                = [0 for i in range(self.NBeams)]
        self.BeamIncidenceAngleAdjustment = [0 for i in range(self.NBeams)]
        self.DetectionInformation         = [0 for i in range(self.NBeams)]
        self.RealtimeCeaningInformation   = [0 for i in range(self.NBeams)]
        self.Reflectivity                 = [0 for i in range(self.NBeams)]

        # now read the variable part of the Record
        rec_fmt = '=fffHBBBbh'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        for i in range(self.NBeams):
            data = self.fileptr.read(rec_len)
            s = rec_unpack(data)
            self.Depth[i] = s[0]
            self.AcrossTrackDistance[i] =  s[1]
            self.AlongTrackDistance[i] = s[2]
            self.DetectionWindowsLength[i] = s[3]
            self.QualityFactor[i] =  s[4]
            self.BeamIncidenceAngleAdjustment[i] =  float (s[5] / 10)
            self.DetectionInformation[i] = s[6]
            self.RealtimeCeaningInformation[i] =  s[7]
            self.Reflectivity[i] = float (s[8] / 10)
            
        rec_fmt = '=BBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
            
        self.ETX                = s[1]
        self.checksum           = s[2]

class P_POSITION:
    def __init__(self, fileptr, offset, bytes):
        self.TypeOfDatagram = 'P'
        self.offset = offset
        self.bytes = bytes
        self.fileptr = fileptr

    def read(self):        
        self.fileptr.seek(self.offset, 0)                
        rec_fmt = '=HLLHHll4HBB'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
        
        self.EMModel         = s[0]
        self.RecordDate      = s[1]
        self.Time            = s[2]
        self.Counter         = s[3]
        self.SerialNumber    = s[4]
        self.Latitude        = float (s[5] / 20000000)
        self.Longitude       = float (s[6] / 10000000)
        self.Quality         = float (s[7] / 100)
        self.SpeedOverGround = float (s[8] / 100)
        self.CourseOverGround= float (s[9] / 100)
        self.Heading         = float (s[10] / 100)
        self.Descriptor      = s[11]
        self.NBytesDatagram  = s[12]

        # now read the variable position part of the Record 
        if self.NBytesDatagram % 2 == 0:
            rec_fmt = '=' + str(self.NBytesDatagram) + 'sBBH'
        else:
            rec_fmt = '=' + str(self.NBytesDatagram) + 'sBH'
            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
        self.DatagramAsReceived = s[0].decode('utf-8').rstrip('\x00')
        if self.NBytesDatagram % 2 == 0:
            self.ETX                = s[2]
            self.checksum           = s[3]
        else:        
            self.ETX                = s[1]
            self.checksum           = s[2]
    
if __name__ == "__main__":
    #open the ALL file for reading by creating a new ALLReader class and passin in the filename to open.
    filename =   "C:/development/all/sampledata/EM2040/GeoFocusEM2040400kHzdual-Rx0.5degx1degPitchStabilised.all"
    r = ALLReader(filename)
    start_time = time.time() # time the process
    pingCount = 0
    waterfall = []
    while r.moreData():
        # read a datagram.  If we support it, return the datagram type and aclass for that datagram
        # The user then needs to call the read() method for the class to undertake a fileread and binary decode.  This keeps the read super quick.
        TypeOfDatagram, datagram = r.readDatagram()

        if TypeOfDatagram == 'P':
            datagram.read()
            print ("Lat: %.5f Lon: %.5f" % (datagram.Latitude, datagram.Longitude))

        if TypeOfDatagram == 'X':
            datagram.read()
            nadirBeam = int(datagram.NBeams / 2)
            print (("Nadir Depth: %.3f AcrossTrack %.3f TransducerDepth %.3f" % (datagram.Depth[nadirBeam], datagram.AcrossTrackDistance[nadirBeam], datagram.TransducerDepth)))

    print("Read Duration: %.3f seconds, pingCount %d" % (time.time() - start_time, pingCount)) # print the processing time. It is handy to keep an eye on processing performance.

    r.rewind()
    print("Complete reading ALL file :-)")
    r.close()    

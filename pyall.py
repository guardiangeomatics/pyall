#name:          pyALL
#created:       August 2016
#by:            p.kennedy@fugro.com
#description:   python module to read a Kongsberg ALL sonar file
#notes:         See main at end of script for example how to use this
#based on ALL Revision R October 2013
#version 3.20

# See readme.md for more details

import pprint
import struct
import os.path
from datetime import datetime
from datetime import timedelta
# import geodetic
import time

class ALLReader:
    ALLPacketHeader_fmt = '=LBBHLL'
    ALLPacketHeader_len = struct.calcsize(ALLPacketHeader_fmt)
    ALLPacketHeader_unpack = struct.Struct(ALLPacketHeader_fmt).unpack_from

    def __init__(self, ALLfileName):
        if not os.path.isfile(ALLfileName):
            print ("file not found:", ALLfileName)
        self.fileName = ALLfileName
        self.fileptr = open(ALLfileName, 'rb')        
        self.fileSize = os.path.getsize(ALLfileName)
        self.recordDate = ""
        self.recordTime = ""

    def __str__(self):
        return pprint.pformat(vars(self))

    def currentRecordDateTime(self):
        date_object = datetime.strptime(str(self.recordDate), '%Y%m%d') + timedelta(0,self.recordTime)
        return date_object

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                
    
    def currentPtr(self):
        return self.fileptr.tell()

    def moreData(self):
        bytesRemaining = self.fileSize - self.fileptr.tell()
        # print ("current file ptr position:", self.fileptr.tell())
        return bytesRemaining
            
    def readDatagramHeader(self):
        curr = self.fileptr.tell()
        data = self.fileptr.read(self.ALLPacketHeader_len)
        s = self.ALLPacketHeader_unpack(data)

        NumberOfBytes   = s[0]
        STX             = s[1]
        TypeOfDatagram  = s[2]
        EMModel         = s[3]
        RecordDate      = s[4]
        RecordTime      = s[5] / 1000
        self.recordDate = RecordDate
        self.recordTime = RecordTime

        # now reset file pointer
        self.fileptr.seek(curr, 0)                
        return NumberOfBytes + 4, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime

    def getRecordCount(self):
        count = 0
        self.rewind()
        while self.moreData():
            NumberOfBytes, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime = self.readDatagramHeader()
            self.fileptr.seek(NumberOfBytes, 1)
            count += 1
        self.rewind()        
        return count

    def readDatagram(self):
        # read the datagram header.  This permits us to skip datagrams we do not support
        NumberOfBytes, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime = self.readDatagramHeader()
        if TypeOfDatagram == 73: # I Installation 
            # create a class for this datagram, but only decode if the resulting class is called by the user.  This makes it much faster
            self.fileptr.seek(NumberOfBytes, 1)
        elif TypeOfDatagram == 80: # P Position
            dg = P_POSITION(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg 
        elif TypeOfDatagram == 88: # X Depth
            dg = X_DEPTH(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg 
        else:
            self.fileptr.seek(NumberOfBytes, 1)
        return 0,0
        
class X_DEPTH:
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'X'
        self.offset = fileptr.tell()
        self.bytes = bytes
        self.fileptr = fileptr
        self.fileptr.seek(bytes, 1)

    def read(self):        
        self.fileptr.seek(self.offset, 0)                
        rec_fmt = '=LBBHLL4Hf2Hf4B'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)

        self.NumberOfBytes   = s[0]
        self.STX             = s[1]
        self.TypeOfDatagram  = s[2]
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        
        self.Heading         = float (s[8] / 100)
        self.SoundSpeedAtTransducer = float (s[9] / 10)
        self.TransducerDepth        = s[10]
        self.NBeams                 = s[11]
        self.NValidDetections       = s[12]
        self.SamplingFrequency      = s[13]
        self.ScanningInfo           = s[14]
        self.spare                  = s[15]

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
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'P'
        self.offset = fileptr.tell()
        self.bytes = bytes
        self.fileptr = fileptr
        self.fileptr.seek(bytes, 1)

    def read(self):        
        self.fileptr.seek(self.offset, 0)                
        rec_fmt = '=LBBHLLHHll4HBB'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
        
        self.NumberOfBytes   = s[0]
        self.STX             = s[1]
        self.TypeOfDatagram  = s[2]
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.Latitude        = float (s[8] / float(20000000))
        self.Longitude       = float (s[9] / float(10000000))
        self.Quality         = float (s[10] / float(100))
        self.SpeedOverGround = float (s[11] / float(100))
        self.CourseOverGround= float (s[12] / float(100))
        self.Heading         = float (s[13] / float(100))
        self.Descriptor      = s[14]
        self.NBytesDatagram  = s[15]

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
        print(r.currentRecordDateTime())

        # if TypeOfDatagram == 'P':
        #     datagram.read()
        #     # print ("Lat: %.5f Lon: %.5f" % (datagram.Latitude, datagram.Longitude))
        # if TypeOfDatagram == 'X':
        #     datagram.read()
        #     nadirBeam = int(datagram.NBeams / 2)
        #     print (("Nadir Depth: %.3f AcrossTrack %.3f TransducerDepth %.3f" % (datagram.Depth[nadirBeam], datagram.AcrossTrackDistance[nadirBeam], datagram.TransducerDepth)))
        #     pingCount += 1

    print("Read Duration: %.3f seconds, pingCount %d" % (time.time() - start_time, pingCount)) # print the processing time. It is handy to keep an eye on processing performance.

    r.rewind()
    print("Complete reading ALL file :-)")
    r.close()    

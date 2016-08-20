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

           
class ALLReader:
    ALLPacketHeader_fmt = '=LBBHLL'
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
            
    def readPacketheader(self):
        data = self.fileptr.read(self.ALLPacketHeader_len)
        s = self.ALLPacketHeader_unpack(data)

        NumberOfBytes   = s[0]
        STX             = s[1]
        TypeOfDatagram  = s[2]
        EMModel         = s[3]
        RecordDate      = s[4]
        RecordTime      = s[5]

        return NumberOfBytes, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime

    def readPacket(self):

        # read the packet header.  This permits us to skip packets we do not support
        NumberOfBytes, STX, TypeOfDatagram, EMModel, RecordDate, RecordTime = self.readPacketheader()

        if TypeOfDatagram == 73: # I Installation records
            # create a class for this datagram, but only decode if the resulting class is called by the user.  This makes it much faster
            pass
        elif TypeOfDatagram == 5:
            pass
        elif TypeOfDatagram == 10:
            pass
        else:
            self.fileptr.seek(NumberOfBytes - 12, 1)
    
        return TypeOfDatagram
    
if __name__ == "__main__":
    #open the ALL file for reading by creating a new ALLReader class and passin in the filename to open.  
    r = ALLReader("C:/development/all/sampledata/EM2040/GeoFocusEM2040400kHzdual-Rx0.5degx1degPitchStabilised.all")
    
    while r.moreData():
        TypeOfDatagram = r.readPacket()

    r.rewind()
    print("Complete reading ALL file :-)")
    r.close()    

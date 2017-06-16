#name:          pyALL
#created:       August 2016
#by:            p.kennedy@fugro.com
#description:   python module to read a Kongsberg ALL sonar file
#notes:         See main at end of script for example how to use this
#based on ALL Revision R October 2013

# See readme.md for more details

import math
import pprint
import struct
import os.path
import time
from datetime import datetime
from datetime import timedelta
# from datetime import timezone
# import geodetic

def main():
    #open the ALL file for reading by creating a new ALLReader class and passin in the filename to open.
    filename =   "C:/Python27/ArcGIS10.3/pyall-master/0314_20170421_222154_SA1702-FE_302.all"
    # filename =   "C:/development/Python/m3Sample.all"
    # filename = "C:/development/python/0004_20110307_041009.all"
    filename = "C:/development/python/0000_20160618_003722_Yolla.all"
    r = ALLReader(filename)
    pingCount = 0
    start_time = time.time() # time the process

    # navigation = r.loadNavigation()
    # print("Load Navigation Duration: %.2fs" % (time.time() - start_time)) # time the process
    # print (navigation)

    while r.moreData():
        # read a datagram.  If we support it, return the datagram type and aclass for that datagram
        # The user then needs to call the read() method for the class to undertake a fileread and binary decode.  This keeps the read super quick.
        TypeOfDatagram, datagram = r.readDatagram()
        # print("TypeOfDatagram:", TypeOfDatagram)
        # print(r.currentRecordDateTime())

        if TypeOfDatagram == 'I':
             datagram.read()
             print (datagram.installationParameters)
            #  print ("Lat: %.5f Lon: %.5f" % (datagram.Latitude, datagram.Longitude))
        if TypeOfDatagram == 'N':
            datagram.read()
            print ("Raw Travel Times Recorded for %d beams" % datagram.NumReceiveBeams)
        if TypeOfDatagram == 'D':
            datagram.read()
            nadirBeam = int(datagram.NBeams / 2)
            print (("Nadir Depth: %.3f AcrossTrack %.3f TransducerDepth %.3f Checksum %s" % (datagram.Depth[nadirBeam], datagram.AcrossTrackDistance[nadirBeam], datagram.TransducerDepth, datagram.checksum)))
        if TypeOfDatagram == 'X':
            datagram.read()
            nadirBeam = int(datagram.NBeams / 2)
            print (("Nadir Depth: %.3f AcrossTrack %.3f TransducerDepth %.3f" % (datagram.Depth[nadirBeam], datagram.AcrossTrackDistance[nadirBeam], datagram.TransducerDepth)))
            pingCount += 1

    print("Read Duration: %.3f seconds, pingCount %d" % (time.time() - start_time, pingCount)) # print the processing time. It is handy to keep an eye on processing performance.

    r.rewind()
    print("Complete reading ALL file :-)")
    r.close()    

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
        try:
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
        except struct.error:
            return 0,0,0,0,0,0
    
    def readDatagramBytes(self, offset, byteCount):
        curr = self.fileptr.tell()
        self.fileptr.seek(offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        data = self.fileptr.read(byteCount)
        self.fileptr.seek(curr, 0)
        return data

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
            dg = I_INSTALLATION(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg 
        elif TypeOfDatagram == 78: # N Angle and Travel Time
            dg = N_TRAVELTIME(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg
        elif TypeOfDatagram == 80: # P Position
            dg = P_POSITION(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg 
        elif TypeOfDatagram == 88: # X Depth
            dg = X_DEPTH(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg 
        elif TypeOfDatagram == 68: # D DEPTH
            dg = D_DEPTH(self.fileptr, NumberOfBytes)
            return dg.TypeOfDatagram, dg
        else:
            dg = UNKNOWN_RECORD(self.fileptr, NumberOfBytes, TypeOfDatagram)
            return dg.TypeOfDatagram, dg
            # self.fileptr.seek(NumberOfBytes, 1)
            # return chr(TypeOfDatagram),0

    def loadNavigation(self):    
        '''loads all the navigation into lists'''
        navigation = []
        selectedPositioningSystem = None
        self.rewind()
        while self.moreData():
            TypeOfDatagram, datagram = self.readDatagram()
            if (TypeOfDatagram == 'P'):
                datagram.read()
                recDate = self.currentRecordDateTime()
                if (selectedPositioningSystem == None):
                    selectedPositioningSystem = datagram.Descriptor
                if (selectedPositioningSystem == datagram.Descriptor):
                    # for python 2.7
                    navigation.append([to_timestamp(recDate), datagram.Latitude, datagram.Longitude])
                    # for python 3.4
                    # navigation.append([recDate.timestamp(), datagram.Latitude, datagram.Longitude])
        self.rewind()
        return navigation

class UNKNOWN_RECORD:
    def __init__(self, fileptr, bytes, typeOfDatagram):
        self.TypeOfDatagram = chr(typeOfDatagram)
        self.offset = fileptr.tell()
        self.bytes = bytes
        self.fileptr = fileptr
        self.fileptr.seek(bytes, 1)
        self.data = ""
    def read(self):
        self.data = self.fileptr.read(self.bytes)
    
class D_DEPTH:
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'D'
        self.offset = fileptr.tell()
        self.bytes = bytes
        self.fileptr = fileptr
        self.fileptr.seek(bytes, 1)
        self.data = ""
    
    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHHHHBBBBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        self.data = self.fileptr.read(rec_len)
        s = rec_unpack(self.data)

        self.NumberOfBytes   = s[0]
        self.STX             = s[1]
        self.TypeOfDatagram  = s[2]
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.Heading                = float (s[8] / float (100))
        self.SoundSpeedAtTransducer = float (s[9] / float (10))
        self.TransducerDepth        = float (s[10] / float (100))
        self.MaxBeams                 = s[11]
        self.NBeams                 = s[12]
        self.ZResolution            = float (s[13] / float (100))
        self.XYResolution           = float (s[14] / float (100))
        self.SamplingFrequency      = s[15]

        self.Depth                        = [0 for i in range(self.NBeams)]
        self.AcrossTrackDistance          = [0 for i in range(self.NBeams)]
        self.AlongTrackDistance           = [0 for i in range(self.NBeams)]
        self.BeamDepressionAngle          = [0 for i in range(self.NBeams)]
        self.BeamAzimuthAngle             = [0 for i in range(self.NBeams)]
        self.Range                        = [0 for i in range(self.NBeams)]
        self.QualityFactor                = [0 for i in range(self.NBeams)]
        self.LengthOfDetectionWindow      = [0 for i in range(self.NBeams)]
        self.Reflectivity                 = [0 for i in range(self.NBeams)]
        self.BeamNumber                   = [0 for i in range(self.NBeams)]

        # now read the variable part of the Record
        if self.EMModel < 700 :
            rec_fmt = '=H3h2H2BbB'
        else:
            rec_fmt = '=4h2H2BbB'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack

        i = 0
        while i < self.NBeams:
            data = self.fileptr.read(rec_len)
            s = rec_unpack(data)
            self.Depth[i]                       = float (s[0] / float (100))
            self.AcrossTrackDistance[i]         = float (s[1] / float (100))
            self.AlongTrackDistance[i]          = float (s[2] / float (100))
            self.BeamDepressionAngle[i]         = float (s[3] / float (100))
            self.BeamAzimuthAngle[i]            = float (s[4] / float (100))
            self.Range[i]                       = float (s[5] / float (100))
            self.QualityFactor[i]               = s[6]
            self.LengthOfDetectionWindow[i]     = s[7]
            self.Reflectivity[i]                = float (s[8] / float (100))
            self.BeamNumber[i]                  = s[9]

            # now do some sanity checks.  We have examples where the Depth and Across track values are NaN
            if (math.isnan(self.Depth[i])):
                self.Depth[i] = 0
            if (math.isnan(self.AcrossTrackDistance[i])):
                self.AcrossTrackDistance[i] = 0
            if (math.isnan(self.AlongTrackDistance[i])):
                self.AlongTrackDistance[i] = 0
            i = i + 1

        rec_fmt = '=bBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)

        self.RangeMultiplier    = s[0]
        self.ETX                = s[1]
        self.checksum           = s[2]

class X_DEPTH:
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'X'
        self.offset = fileptr.tell()
        self.bytes = bytes
        self.fileptr = fileptr
        self.fileptr.seek(bytes, 1)
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)                
        rec_fmt = '=LBBHLL4Hf2Hf4B'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        self.data = self.fileptr.read(rec_len)
        s = rec_unpack(self.data)

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
        self.RealtimeCleaningInformation   = [0 for i in range(self.NBeams)]
        self.Reflectivity                 = [0 for i in range(self.NBeams)]

        # # now read the variable part of the Record
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
            self.RealtimeCleaningInformation[i] =  s[7]
            self.Reflectivity[i] = float (s[8] / 10)

            # now do some sanity checks.  We have examples where the Depth and Across track values are NaN
            if (math.isnan(self.Depth[i])):
                self.Depth[i] = 0
            if (math.isnan(self.AcrossTrackDistance[i])):
                self.AcrossTrackDistance[i] = 0
            if (math.isnan(self.AlongTrackDistance[i])):
                self.AlongTrackDistance[i] = 0

        rec_fmt = '=BBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
            
        self.ETX                = s[1]
        self.checksum           = s[2]

class P_POSITION:
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'P'       # assign the KM code for this datagram type
        self.offset = fileptr.tell()    # remember where this packet resides in the file so we can return if needed
        self.bytes = bytes              # remember how many bytes this packet contains
        self.fileptr = fileptr          # remember the file pointer so we do not need to pass from the host process
        self.fileptr.seek(bytes, 1)     # move the file pointer to the end of the record so we can skip as the default actions
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        rec_fmt = '=LBBHLLHHll4HBB'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        self.data = self.fileptr.read(rec_len)   # read the record from disc
        bytesRead = rec_len
        s = rec_unpack(self.data)
        
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
        bytesRead += rec_len
        s = rec_unpack(data)
        self.DatagramAsReceived = s[0].decode('utf-8').rstrip('\x00')
        if self.NBytesDatagram % 2 == 0:
            self.ETX                = s[2]
            self.checksum           = s[3]
        else:        
            self.ETX                = s[1]
            self.checksum           = s[2]
        
        #read any trailing bytes.  We have seen the need for this with some .all files.
        if bytesRead < self.bytes:
            self.fileptr.read(int(self.bytes - bytesRead))

class N_TRAVELTIME:
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'N'
        self.offset = fileptr.tell()
        self.bytes = bytes
        self.fileptr = fileptr
        self.fileptr.seek(bytes, 1)
        self.data = ""

    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHHHHHfL'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        self.data = self.fileptr.read(rec_len)
        bytesRead = rec_len
        s = rec_unpack(self.data)

        self.NumberOfBytes   = s[0]
        self.STX             = s[1]
        self.TypeOfDatagram  = s[2]
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]
        self.PingCounter     = s[6]
        self.SerialNumber    = s[7]
        self.SoundSpeedAtTransducer = s[8]
        self.NumTransitSector= s[9]
        self.NumReceiveBeams = s[10]
        self.NumValidDetect  = s[11]
        self.SampleFrequency = float (s[12])
        self.DScale          = s[13]

        self.TiltAngle                    = [0 for i in range(self.NumTransitSector)]
        self.FocusRange                   = [0 for i in range(self.NumTransitSector)]
        self.SignalLength                 = [0 for i in range(self.NumTransitSector)]
        self.SectorTransmitDelay          = [0 for i in range(self.NumTransitSector)]
        self.CentreFrequency              = [0 for i in range(self.NumTransitSector)]
        self.MeanAbsorption               = [0 for i in range(self.NumTransitSector)]
        self.SignalWaveformID             = [0 for i in range(self.NumTransitSector)]
        self.TransmitSectorNumberTX       = [0 for i in range(self.NumTransitSector)]
        self.SignalBandwidth              = [0 for i in range(self.NumTransitSector)]

        self.BeamPointingAngle            = [0 for i in range(self.NumReceiveBeams)]
        self.TransmitSectorNumber         = [0 for i in range(self.NumReceiveBeams)]
        self.DetectionInfo                = [0 for i in range(self.NumReceiveBeams)]
        self.DetectionWindow              = [0 for i in range(self.NumReceiveBeams)]
        self.QualityFactor                = [0 for i in range(self.NumReceiveBeams)]
        self.DCorr                        = [0 for i in range(self.NumReceiveBeams)]
        self.TwoWayTravelTime             = [0 for i in range(self.NumReceiveBeams)]
        self.Reflectivity                 = [0 for i in range(self.NumReceiveBeams)]
        self.RealtimeCleaningInformation  = [0 for i in range(self.NumReceiveBeams)]
        self.Spare                        = [0 for i in range(self.NumReceiveBeams)]

        # # now read the variable part of the Transmit Record
        rec_fmt = '=hHfffHBBf'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        for i in range(self.NumTransitSector):
            data = self.fileptr.read(rec_len)
            bytesRead += rec_len
            s = rec_unpack(data)
            self.TiltAngle[i] = float (s[0]) / float (100)
            self.FocusRange[i] =  s[1]
            self.SignalLength[i] = float (s[2])
            self.SectorTransmitDelay[i] = float(s[3])
            self.CentreFrequency[i] =  float (s[4])
            self.MeanAbsorption[i] =  s[5]
            self.SignalWaveformID[i] = s[6]
            self.TransmitSectorNumberTX[i] =  s[7]
            self.SignalBandwidth[i] = float (s[8])
        
        # now read the variable part of the recieve record
        rx_rec_fmt = '=hBBHBbfhbB'
        rx_rec_len = struct.calcsize(rx_rec_fmt)
        rx_rec_unpack = struct.Struct(rx_rec_fmt).unpack
        for i in range(self.NumReceiveBeams):
            data = self.fileptr.read(rx_rec_len)
            bytesRead += rx_rec_len
            rx_s = rx_rec_unpack(data)
            self.BeamPointingAngle[i] = float (rx_s[0]) / float (100)
            self.TransmitSectorNumber[i] = rx_s[1]
            self.DetectionInfo[i] = rx_s[2]
            self.DetectionWindow[i] = rx_s[3]
            self.QualityFactor[i] = rx_s[4]
            self.DCorr[i] = rx_s[5]
            self.TwoWayTravelTime[i] = float (rx_s[6])
            self.Reflectivity[i] = rx_s[7]
            self.RealtimeCleaningInformation[i] = rx_s[8]
            self.Spare[i]                       = rx_s[9]
        
        rec_fmt = '=BBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
            
        self.ETX                = s[1]
        self.checksum           = s[2]

class I_INSTALLATION:
    def __init__(self, fileptr, bytes):
        self.TypeOfDatagram = 'I'       # assign the KM code for this datagram type
        self.offset = fileptr.tell()    # remember where this packet resides in the file so we can return if needed
        self.bytes = bytes              # remember how many bytes this packet contains
        self.fileptr = fileptr          # remember the file pointer so we do not need to pass from the host process
        self.fileptr.seek(bytes, 1)     # move the file pointer to the end of the record so we can skip as the default actions
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        rec_fmt = '=LBBHLL3H'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        self.data = self.fileptr.read(rec_len)   # read the record from disc
        bytesRead = rec_len
        s = rec_unpack(self.data)
        
        self.NumberOfBytes   = s[0]
        self.STX             = s[1]
        self.TypeOfDatagram  = s[2]
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]
        self.SurveyLineNumber= s[6]
        self.SerialNumber    = s[7]
        self.SecondarySerialNumber = s[8]

        totalAsciiBytes = self.bytes - rec_len; # we do not need to read the header twice
        data = self.fileptr.read(totalAsciiBytes)   # read the record from disc
        bytesRead = bytesRead + totalAsciiBytes 
        parameters = data.decode('utf-8', errors="ignore").split(",")
        self.installationParameters = {}
        for p in parameters:
            parts = p.split("=")
            if len(parts) > 1:
                self.installationParameters[parts[0]] = parts[1].strip()

        #read any trailing bytes.  We have seen the need for this with some .all files.
        if bytesRead < self.bytes:
            self.fileptr.read(int(self.bytes - bytesRead))

def to_timestamp(recordDate):
    return (recordDate - datetime(1970, 1, 1)).total_seconds()

def from_timestamp(unixtime):
    return datetime(1970, 1 ,1) + timedelta(unixtime)

if __name__ == "__main__":
        main()

#name:          pyALL
#created:       August 2016
#by:            p.kennedy@fugro.com
#description:   python module to read a Kongsberg ALL sonar file
#notes:         See main at end of script for example how to use this
#based on ALL Revision R October 2013

# See readme.md for more details

import ctypes
import math
import pprint
import struct
import os.path
import time
from datetime import datetime
from datetime import timedelta

def main():
    #open the ALL file for reading by creating a new ALLReader class and passin in the filename to open.
    # filename =   "C:/Python27/ArcGIS10.3/pyall-master/0314_20170421_222154_SA1702-FE_302.all"
    # filename =   "C:/development/Python/m3Sample.all"
    # filename = "C:/development/python/0004_20110307_041009.all"
    filename = "C:/development/python/sample.all"
    # filename = "d:/projects/RVInvestigator/0073_20161001_103120_Investigator_em710.all"
    # filename = "C:/projects/RVInvestigator/0016_20160821_150810_Investigator_em710.all"
    # filename = "c:/projects/carisworldtour/preprocess/0010_20110308_194752.all"

    r = ALLReader(filename)
    pingCount = 0
    start_time = time.time() # time the process

    # navigation = r.loadNavigation()
    # print("Load Navigation Duration: %.2fs" % (time.time() - start_time)) # time the process
    # print (navigation)

    while r.moreData():
        # read a datagram.  If we support it, return the datagram type and aclass for that datagram
        # The user then needs to call the read() method for the class to undertake a fileread and binary decode.  This keeps the read super quick.
        typeOfDatagram, datagram = r.readDatagram()
        print(typeOfDatagram, end='')
        
        rawbytes = r.readDatagramBytes(datagram.offset, datagram.numberOfBytes)
        crc = crc16(rawbytes[4:-2])
        # 51155
        # # print(r.currentRecordDateTime())

        if typeOfDatagram == '3':
            datagram.read()
            print (datagram.data)
            continue

        if typeOfDatagram == 'A':
            datagram.read()
            # for a in datagram.Attitude:
            #     print ("%.5f, %.3f, %.3f, %.3f, %.3f" % (r.to_timestamp(r.to_DateTime(a[0], a[1])), a[3], a[4], a[5], a[6]))
            continue

        if typeOfDatagram == 'C':
            datagram.read()
            continue

        if typeOfDatagram == 'D':
            datagram.read()
            nadirBeam = int(datagram.NBeams / 2)
            # print (("Nadir Depth: %.3f AcrossTrack %.3f TransducerDepth %.3f Checksum %s" % (datagram.Depth[nadirBeam], datagram.AcrossTrackDistance[nadirBeam], datagram.TransducerDepth, datagram.checksum)))
            continue
        
        if typeOfDatagram == 'H':
            datagram.read()

        if typeOfDatagram == 'i':
            datagram.read()
            continue

        if typeOfDatagram == 'I':
            datagram.read()
            #  print (datagram.installationParameters)
            #  print ("Lat: %.5f Lon: %.5f" % (datagram.Latitude, datagram.Longitude))
            continue

        if typeOfDatagram == 'n':
            datagram.read()
            continue

        if typeOfDatagram == 'N':
            datagram.read()
            # print ("Raw Travel Times Recorded for %d beams" % datagram.NumReceiveBeams)
            continue

        if typeOfDatagram == 'R':
            datagram.read()
            continue

        if typeOfDatagram == 'U':
            datagram.read()
            continue

        if typeOfDatagram == 'X':
            datagram.read()
            nadirBeam = int(datagram.NBeams / 2)
            # print (("Nadir Depth: %.3f AcrossTrack %.3f TransducerDepth %.3f" % (datagram.Depth[nadirBeam], datagram.AcrossTrackDistance[nadirBeam], datagram.TransducerDepth)))
            pingCount += 1
            continue

        if typeOfDatagram == 'Y':
            datagram.read()
            continue

    print("Read Duration: %.3f seconds, pingCount %d" % (time.time() - start_time, pingCount)) # print the processing time. It is handy to keep an eye on processing performance.

    r.rewind()
    print("Complete reading ALL file :-)")
    r.close()    

class ALLReader:
    '''class to read a Kongsberg EM multibeam .all file'''
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
        '''return a python date object from the current datagram objects raw date and time fields '''
        date_object = datetime.strptime(str(self.recordDate), '%Y%m%d') + timedelta(0,self.recordTime)
        return date_object

    def to_DateTime(self, recordDate, recordTime):
        '''return a python date object from a split date and time record'''
        date_object = datetime.strptime(str(recordDate), '%Y%m%d') + timedelta(0,recordTime)
        return date_object

    # def to_timestamp(self, dateObject):
    #     '''return a unix timestamp from a python date object'''
    #     return (dateObject - datetime(1970, 1, 1)).total_seconds()


    def close(self):
        '''close the current file'''
        self.fileptr.close()
        
    def rewind(self):
        '''go back to start of file'''
        self.fileptr.seek(0, 0)                
    
    def currentPtr(self):
        '''report where we are in the file reading process'''
        return self.fileptr.tell()

    def moreData(self):
        '''report how many more bytes there are to read from the file'''
        return self.fileSize - self.fileptr.tell()
            
    def readDatagramHeader(self):
        '''read the common header for any datagram'''
        try:
            curr = self.fileptr.tell()
            data = self.fileptr.read(self.ALLPacketHeader_len)
            s = self.ALLPacketHeader_unpack(data)

            numberOfBytes   = s[0]
            STX             = s[1]
            typeOfDatagram  = chr(s[2])
            EMModel         = s[3]
            RecordDate      = s[4]
            RecordTime      = float(s[5]/1000.0)
            self.recordDate = RecordDate
            self.recordTime = RecordTime

            # now reset file pointer
            self.fileptr.seek(curr, 0)
    
            # we need to add 4 bytes as the message does not contain the 4 bytes used to hold the size of the message
            # trap corrupt datagrams at the end of a file.  We see this in EM2040 systems.
            if (curr + numberOfBytes + 4 ) > self.fileSize:
                numberOfBytes = self.fileSize - curr - 4
                typeOfDatagram = 'XXX'
                return numberOfBytes + 4, STX, typeOfDatagram, EMModel, RecordDate, RecordTime
    
            return numberOfBytes + 4, STX, typeOfDatagram, EMModel, RecordDate, RecordTime
        except struct.error:
            return 0,0,0,0,0,0
    
    def readDatagramBytes(self, offset, byteCount):
        '''read the entire raw bytes for the datagram without changing the file pointer.  this is used for file conditioning'''
        curr = self.fileptr.tell()
        self.fileptr.seek(offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        data = self.fileptr.read(byteCount)
        self.fileptr.seek(curr, 0)
        return data

    def getRecordCount(self):
        '''read through the entire file as fast as possible to get a count of all records.  useful for progress bars so user can see what is happening'''
        count = 0
        self.rewind()
        while self.moreData():
            numberOfBytes, STX, typeOfDatagram, EMModel, RecordDate, RecordTime = self.readDatagramHeader()
            self.fileptr.seek(numberOfBytes, 1)
            count += 1
        self.rewind()        
        return count

    def readDatagram(self):
        '''read the datagram header.  This permits us to skip datagrams we do not support'''
        numberOfBytes, STX, typeOfDatagram, EMModel, RecordDate, RecordTime = self.readDatagramHeader()
        
        if typeOfDatagram == '3': # 3_EXTRA PARAMETERS DECIMAL 51
            dg = E_EXTRA(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg
        if typeOfDatagram == 'A': # A ATTITUDE
            dg = A_ATTITUDE(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg
        if typeOfDatagram == 'C': # C Clock 
            dg = C_CLOCK(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'D': # D DEPTH
            dg = D_DEPTH(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg
        if typeOfDatagram == 'H': # H Height  
            dg = H_HEIGHT(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'I': # I Installation (Start)
            dg = I_INSTALLATION(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'i': # i Installation (Stop)
            dg = I_INSTALLATION(self.fileptr, numberOfBytes)
            dg.typeOfDatagram = 'i' #override with the install stop code
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'n': # n ATTITUDE
            dg = n_ATTITUDE(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg
        if typeOfDatagram == 'N': # N Angle and Travel Time
            dg = N_TRAVELTIME(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg
        if typeOfDatagram == 'R': # R_RUNTIME
            dg = R_RUNTIME(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'P': # P Position
            dg = P_POSITION(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'U': # U Sound Velocity
            dg = U_SVP(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg
        if typeOfDatagram == 'X': # X Depth
            dg = X_DEPTH(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        if typeOfDatagram == 'Y': # Y_SeabedImage
            dg = Y_SEABEDIMAGE(self.fileptr, numberOfBytes)
            return dg.typeOfDatagram, dg 
        else:
            dg = UNKNOWN_RECORD(self.fileptr, numberOfBytes, typeOfDatagram)
            return dg.typeOfDatagram, dg
            # self.fileptr.seek(numberOfBytes, 1)

###############################################################################
    def loadInstallationRecords(self):    
        '''loads all the navigation into lists'''
        
        installStart = None
        installStop = None
        initialMode = None
        self.rewind()
        while self.moreData():
            typeOfDatagram, datagram = self.readDatagram()
            # print (typeOfDatagram, end='')
            if (typeOfDatagram == 'I'):
                installStart = self.readDatagramBytes(datagram.offset, datagram.numberOfBytes)
            if (typeOfDatagram == 'i'):
                datagram.read()
                installStop = self.readDatagramBytes(datagram.offset, datagram.numberOfBytes)
            if (initialMode == None and typeOfDatagram == 'R'):
                datagram.read()
                initialMode = datagram.DepthMode
        self.rewind()
        return installStart, installStop, initialMode        

###############################################################################
    def loadNavigation(self, firstRecordOnly=False):    
        '''loads all the navigation into lists'''
        navigation = []
        selectedPositioningSystem = None
        self.rewind()
        while self.moreData():
            typeOfDatagram, datagram = self.readDatagram()
            if (typeOfDatagram == 'P'):
                datagram.read()
                recDate = self.currentRecordDateTime()
                if (selectedPositioningSystem == None):
                    selectedPositioningSystem = datagram.Descriptor
                if (selectedPositioningSystem == datagram.Descriptor):
                    # for python 2.7
                    navigation.append([to_timestamp(recDate), datagram.Latitude, datagram.Longitude])
                    # for python 3.4
                    # navigation.append([recDate.timestamp(), datagram.Latitude, datagram.Longitude])
                    
                    if firstRecordOnly: #we only want the first record, so reset the file pointer and quit
                        self.rewind()
                        return navigation
        self.rewind()
        return navigation

    def getDatagramName(typeOfDatagram):
        '''Convert the datagram type from the code to a user readable string.  Handy for displaying to the user'''
        #Multibeam Data
        if (typeOfDatagram == 'D'):
            return "D_Depth"
        if (typeOfDatagram == 'X'):
            return "XYZ_Depth"
        if (typeOfDatagram == 'K'):
            return "K_CentralBeam"
        if (typeOfDatagram == 'F'):
            return "F_RawRange"
        if (typeOfDatagram == 'f'):
            return "f_RawRange"
        if (typeOfDatagram == 'N'):
            return "N_RawRange"
        if (typeOfDatagram == 'S'):
            return "S_SeabedImage"
        if (typeOfDatagram == 'Y'):
            return "Y_SeabedImage"
        if (typeOfDatagram == 'k'):
            return "k_WaterColumn"
        if (typeOfDatagram == 'O'):
            return "O_QualityFactor"

        # ExternalSensors
        if (typeOfDatagram == 'A'):
            return "A_Attitude"
        if (typeOfDatagram == 'n'):
            return "network_Attitude"
        if (typeOfDatagram == 'C'):
            return "C_Clock"
        if (typeOfDatagram == 'h'):
            return "h_Height"
        if (typeOfDatagram == 'H'):
            return "H_Heading"
        if (typeOfDatagram == 'P'):
            return "P_Position"
        if (typeOfDatagram == 'E'):
            return "E_SingleBeam"
        if (typeOfDatagram == 'T'):
            return "T_Tide"

        # SoundSpeed
        if (typeOfDatagram == 'G'):
            return "G_SpeedSoundAtHead"
        if (typeOfDatagram == 'U'):
            return "U_SpeedSoundProfile"
        if (typeOfDatagram == 'W'):
            return "W_SpeedSOundProfileUsed"

        # Multibeam parameters       
        if (typeOfDatagram == 'I'):
            return "I_Installation_Start"
        if (typeOfDatagram == 'i'):
            return "i_Installation_Stop"
        if (typeOfDatagram == R):
            return "R_Runtime"
        if (typeOfDatagram == J):
            return "J_TransducerTilt"
        if (typeOfDatagram == '3'):
            return "3_ExtraParameters"

        # PU information and status
        if (typeOfDatagram == '0'):
            return "0_PU_ID"
        if (typeOfDatagram == '1'):
            return "1_PU_Status"
        if (typeOfDatagram == 'B'):
            return "B_BIST_Result"


###############################################################################
class cBeam:
    def __init__(self, beamDetail, angle):
        self.sortingDirection       = beamDetail[0]
        self.detectionInfo          = beamDetail[1]
        self.numberOfSamplesPerBeam = beamDetail[2]
        self.centreSampleNumber     = beamDetail[3]
        self.sector                 = 0
        self.takeOffAngle           = angle     # used for ARC computation
        self.sampleSum              = 0         # used for backscatter ARC computation process
        self.samples                = []

###############################################################################
class A_ATTITUDE_ENCODER:
    def __init__(self):
        self.data = 0

    def encode(self, recordsToAdd, counter):
        '''Encode a list of attitude records where the format is timestamp, rool, pitch, heave heading'''
        if (len(recordsToAdd) == 0):
            return

        fullDatagram = bytearray()

        header_fmt = '=LBBHLLHHH'
        header_len = struct.calcsize(header_fmt)

        rec_fmt = "HHhhhH"
        rec_len = struct.calcsize(rec_fmt)

        footer_fmt = '=BBH'
        footer_len = struct.calcsize(footer_fmt)

        STX = 2
        typeOfDatagram = 65
        model = 2045

        serialNumber = 999
        numEntries = len(recordsToAdd)

        fullDatagramByteCount = header_len + (rec_len*len(recordsToAdd)) + footer_len

        firstRecordTimestamp = float(recordsToAdd[0][0]) #we need to know the first reord timestamp as all observations are milliseconds from that time
        firstRecordDate = from_timestamp(firstRecordTimestamp)

        recordDate = int(dateToKongsbergDate(firstRecordDate))
        recordTime = int(dateToSecondsSinceMidnight(firstRecordDate)*1000)
        # we need to deduct 4 bytes as the field does not account for the 4-byte message length data which precedes the message
        header = struct.pack(header_fmt, fullDatagramByteCount-4, STX, typeOfDatagram, model, recordDate, recordTime, counter, serialNumber, numEntries)
        fullDatagram = fullDatagram + header
        
        # now pack avery record from the list
        for record in recordsToAdd:
            timeMillisecs = round((float(record[0]) - firstRecordTimestamp) * 1000) # compute the millisecond offset of the record from the first record in the datagram
            sensorStatus = 0
            roll    = 0.0 #float(record[1])
            pitch   = 0.0 #float(record[2])
            heave   = float(record[1]) * 10 # heave in m.  multiple by 10 for testing only !! pkpk
            heading = 0.0 # float(record[4])
            bodyRecord = struct.pack(rec_fmt, timeMillisecs, sensorStatus, int(roll*100), int(pitch*100), int(heave*100), int(heading*100))
            fullDatagram = fullDatagram + bodyRecord

        # now do the footer 
        systemDescriptor = 30
        ETX = 3
        checksum = 0
        footer = struct.pack('=BBH', systemDescriptor, ETX, checksum)
        fullDatagram = fullDatagram + footer

        # TEST THE CRC CODE pkpk
        # c = CRC16()
        # chk = c.calculate(fullDatagram)

        return fullDatagram

###############################################################################
class A_ATTITUDE:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'A'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""
    
    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.NumberEntries   = s[8]

        rec_fmt = '=HHhhhH'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack

        # we need to store all the attitude data in a list 
        self.Attitude = [0 for i in range(self.NumberEntries)]

        i = 0
        while i < self.NumberEntries:
            data = self.fileptr.read(rec_len)
            s = rec_unpack(data)
            self.Attitude[i] = [self.RecordDate, self.Time + s[0]/1000, s[1], s[2]/100.0, s[3]/100.0, s[4]/100.0, s[5]/100.0]
            i = i + 1

        rec_fmt = '=BBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)
            
        self.systemDescriptor  = s[0]
        self.ETX                = s[1]
        self.checksum           = s[2]

###############################################################################
class C_CLOCK:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'C'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""

    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHLLBBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        # bytesRead = rec_len
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.ClockCounter    = s[6]
        self.SerialNumber    = s[7]

        self.ExternalDate       = s[8]
        self.ExternalTime       = s[9]
        self.PPS                = s[10]
        self.ETX                = s[11]
        self.checksum           = s[12]
    

###############################################################################
class D_DEPTH:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'D'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""
    
    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHHHHBBBBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
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

###############################################################################
class E_EXTRA:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = '3'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.ExtraData = ""
    
    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.ContentIdentifier   = s[8]

        # now read the variable position part of the Record 
        if self.numberOfBytes % 2 != 0:
            bytesToRead = self.numberOfBytes - rec_len  - 5 # 'sBBH'
        else:
            bytesToRead = self.numberOfBytes - rec_len  - 4 # 'sBH'
        
        # now read the block of data whatever it may contain
        self.data = self.fileptr.read(bytesToRead)

        # # now spare byte only if necessary
        # if self.numberOfBytes % 2 != 0:
        #     self.fileptr.read(1)        

        # read an empty byte
        self.fileptr.read(1)        

        # now read the footer
        self.ETX, self.checksum = readFooter(self.numberOfBytes, self.fileptr)

###############################################################################
class H_HEIGHT:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'h'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""
        self.Height = 0
        self.HeightType = 0

    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHlBBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.Height          = float (s[8] / float (100))
        self.HeightType      = s[9]

        # now read the footer
        self.ETX, self.checksum = readFooter(self.numberOfBytes, self.fileptr)

###############################################################################
class H_HEIGHT_ENCODER:
    def encode(self, height, recordDate, recordTime, counter):
        '''Encode a Height datagram record'''
        rec_fmt = '=LBBHLLHHlBBH'
        rec_len = struct.calcsize(rec_fmt)
        heightType = 0 #0 = the height of the waterline at the vertical datum (from KM datagram manual)
        serialNumber = 999
        STX = 2
        typeOfDatagram = 'h'
        ETX = 3
        checksum = 0
        model = 2045 #needs to be a sensible value to record is valid.  Maybe would be better to pass this from above
        header = struct.pack(rec_fmt, rec_len-4, STX, ord(typeOfDatagram), model, int(recordDate), int(recordTime), counter, serialNumber, int(height * 100), int(heightType), ETX, checksum)
        return header

###############################################################################
class I_INSTALLATION:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'I'       # assign the KM code for this datagram type
        self.offset = fileptr.tell()    # remember where this packet resides in the file so we can return if needed
        self.numberOfBytes = numberOfBytes              # remember how many bytes this packet contains. This includes the first 4 bytes represnting the number of bytes inthe datagram
        self.fileptr = fileptr          # remember the file pointer so we do not need to pass from the host process
        self.fileptr.seek(numberOfBytes, 1)     # move the file pointer to the end of the record so we can skip as the default actions
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        rec_fmt = '=LBBHLL3H'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
           # read the record from disc
        bytesRead = rec_len
        s = rec_unpack(self.fileptr.read(rec_len))
        
        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.SurveyLineNumber= s[6]
        self.SerialNumber    = s[7]
        self.SecondarySerialNumber = s[8]

        totalAsciiBytes = self.numberOfBytes - rec_len; # we do not need to read the header twice
        data = self.fileptr.read(totalAsciiBytes)   # read the record from disc
        bytesRead = bytesRead + totalAsciiBytes 
        parameters = data.decode('utf-8', errors="ignore").split(",")
        self.installationParameters = {}
        for p in parameters:
            parts = p.split("=")
            if len(parts) > 1:
                self.installationParameters[parts[0]] = parts[1].strip()

        #read any trailing bytes.  We have seen the need for this with some .all files.
        if bytesRead < self.numberOfBytes:
            self.fileptr.read(int(self.numberOfBytes - bytesRead))

###############################################################################
class n_ATTITUDE:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'n'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""
    
    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHHbB'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.NumberEntries   = s[8]
        self.SystemDescriptor= s[9]

        rec_fmt = '=HhhhHB'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack

        # we need to store all the attitude data in a list 
        self.Attitude = [0 for i in range(self.NumberEntries)]

        i = 0
        while i < self.NumberEntries:
            data = self.fileptr.read(rec_len)
            s = rec_unpack(data)

            inputTelegramSize = s[5]
            data = self.fileptr.read(inputTelegramSize)
            self.Attitude[i] = [self.RecordDate, self.Time + s[0]/1000, s[1], s[2]/100.0, s[3]/100.0, s[4]/100.0, s[5]/100.0, data]
            i = i + 1

        # # now spare byte only if necessary
        # if self.numberOfBytes % 2 != 0:
        #     self.fileptr.read(1)        

        # read an empty byte
        self.fileptr.read(1)        

        # now read the footer
        self.ETX, self.checksum = readFooter(self.numberOfBytes, self.fileptr)

###############################################################################
class N_TRAVELTIME:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'N'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""

    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHHHHHfL'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        bytesRead = rec_len
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
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
            rx_s = rx_rec_unpack(data)
            bytesRead += rx_rec_len
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
###############################################################################
class P_POSITION:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'P'       # assign the KM code for this datagram type
        self.offset = fileptr.tell()    # remember where this packet resides in the file so we can return if needed
        self.numberOfBytes = numberOfBytes              # remember how many bytes this packet contains
        self.fileptr = fileptr          # remember the file pointer so we do not need to pass from the host process
        self.fileptr.seek(numberOfBytes, 1)     # move the file pointer to the end of the record so we can skip as the default actions
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        rec_fmt = '=LBBHLLHHll4HBB'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        # bytesRead = rec_len
        s = rec_unpack(self.fileptr.read(rec_len))
        
        self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
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

        # now read the block of data whatever it may contain
        self.data = self.fileptr.read(self.NBytesDatagram)

        # now spare byte only if necessary
        if (rec_len + self.NBytesDatagram + 3) % 2 != 0:
            self.fileptr.read(1)        

        self.ETX, self.checksum = readFooter(self.numberOfBytes, self.fileptr)

def readFooter(numberOfBytes, fileptr):
        rec_fmt = '=BH'
            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(fileptr.read(rec_len))
        ETX                = s[0]
        checksum           = s[1]
        # self.DatagramAsReceived = s[0].decode('utf-8').rstrip('\x00')
        # if numberOfBytes % 2 == 0:
        #     # skip the spare byte
        #     ETX                = s[2]
        #     checksum           = s[3]
        # else:        
        #     ETX                = s[1]
        #     checksum           = s[2]
        
        # #read any trailing bytes.  We have seen the need for this with some .all files.
        # if bytesRead < self.numberOfBytes:
        #     self.fileptr.read(int(self.numberOfBytes - bytesRead))

        return ETX, checksum

###############################################################################
class R_RUNTIME:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'R'       # assign the KM code for this datagram type
        self.offset = fileptr.tell()    # remember where this packet resides in the file so we can return if needed
        self.numberOfBytes = numberOfBytes              # remember how many bytes this packet contains
        self.fileptr = fileptr          # remember the file pointer so we do not need to pass from the host process
        self.fileptr.seek(numberOfBytes, 1)     # move the file pointer to the end of the record so we can skip as the default actions
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)   # move the file pointer to the start of the record so we can read from disc              
        rec_fmt = '=LBBHLLHHBBBBBBHHHHHbBBBBBHBBBBHHBBH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        data = self.fileptr.read(rec_len)
        s = rec_unpack(data)

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]/1000
        self.Counter         = s[6]
        self.SerialNumber    = s[7]

        self.operatorStationStatus = s[8]
        # if operatorStationStatus >>
        self.processingUnitStatus   = s[9]
        self.BSPStatus              = s[10]
        self.sonarHeadStatus        = s[11]
        self.mode                   = s[12]
        self.filterIdentifier       = s[13]
        self.minimumDepth           = s[14]
        self.maximumDepth           = s[15]
        self.absorptionCoefficient  = s[16]
        self.transmitPulseLength    = s[17]
        self.transmitBeamWidth      = s[18]
        self.transmitPower          = s[19]
        self.receiveBeamWidth       = s[20]
        self.receiveBandwidth       = s[21]
        self.mode2                  = s[22]
        self.tvg                    = s[23]
        self.sourceOfSpeedSound     = s[24]
        self.maximumPortWidth       = s[25]
        self.beamSpacing            = s[26]
        self.maximumPortCoverageDegrees     = s[27]
        self.yawAndPitchStabilisationMode   = s[28]
        self.maximumStbdCoverageDegrees     = s[29]
        self.maximumStbdWidth               = s[30]
        self.transmitAAlongTilt             = s[31]
        self.filterIdentifier2               = s[32]
        self.ETX                            = s[33]
        self.checksum                       = s[34]

        self.DepthMode = "VeryShallow"
        if (isBitSet(self.mode, 0)):
            self.DepthMode = "Shallow"
        if (isBitSet(self.mode, 1)):
            self.DepthMode = "Medium"
        if (isBitSet(self.mode, 0) & (isBitSet(self.mode, 1))):
            self.DepthMode = "VeryDeep"
        if (isBitSet(self.mode, 2)):
            self.DepthMode = "VeryDeep"
        if (isBitSet(self.mode, 0) & (isBitSet(self.mode, 2))):
            self.DepthMode = "VeryDeep"

        if str(self.EMModel) in 'EM2040, EM2045':
            self.DepthMode = "200kHz"
            if (isBitSet(self.mode, 0)):
                self.DepthMode = "300kHz"
            if (isBitSet(self.mode, 1)):
                self.DepthMode = "400kHz"
            
        self.TXPulseForm = "CW"
        if (isBitSet(self.mode, 4)):
            self.TXPulseForm = "Mixed"
        if (isBitSet(self.mode, 5)):
            self.TXPulseForm = "FM"

        self.dualSwathMode = "Off";
        if (isBitSet(self.mode, 6)):
            dualSwathMode = "Fixed";
        if (isBitSet(self.mode, 7)):
            dualSwathMode = "Dynamic";

        self.filterSetting = "SpikeFilterOff";
        if (isBitSet(self.filterIdentifier, 0)):
            self.filterSetting = "SpikeFilterWeak";
        if (isBitSet(self.filterIdentifier, 1)):
            self.filterSetting = "SpikeFilterMedium";
        if (isBitSet(self.filterIdentifier, 0) & (isBitSet(self.filterIdentifier, 1))):
            self.filterSetting = "SpikeFilterMedium";
        if (isBitSet(self.filterIdentifier, 2)):
            self.filterSetting += "+SlopeOn";
        if (isBitSet(self.filterIdentifier, 3)):
            self.filterSetting += "+SectorTrackingOn";
        if ((not isBitSet(self.filterIdentifier, 4)) & (not isBitSet(self.filterIdentifier, 7))):
            self.filterSetting += "+RangeGatesNormal";
        if ((isBitSet(self.filterIdentifier, 4)) & (not isBitSet(self.filterIdentifier, 7))):
            self.filterSetting += "+RangeGatesLarge";
        if ((not isBitSet(self.filterIdentifier, 4)) & (isBitSet(self.filterIdentifier, 7))):
            self.filterSetting += "+RangeGatesSmall";
        if (isBitSet(self.filterIdentifier, 5)):
            self.filterSetting += "+AerationFilterOn";
        if (isBitSet(self.filterIdentifier, 6)):
            self.filterSetting += "+InterferenceFilterOn";
        return

###############################################################################
class UNKNOWN_RECORD:
    '''used as a convenience tool for datagrams we have no bespoke classes.  Better to make a bespoke class'''
    def __init__(self, fileptr, numberOfBytes, typeOfDatagram):
        self.typeOfDatagram = typeOfDatagram
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""
    def read(self):
        self.data = self.fileptr.read(self.numberOfBytes)

###############################################################################
class U_SVP:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'U'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = []
    
    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHLLHH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.ProfileDate     = s[8]
        self.ProfileTime     = s[9]
        self.NEntries        = s[10]
        self.DepthResolution = s[11]

        rec_fmt = '=LL'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack

        i = 0
        for i in range (self.NEntries):
            data = self.fileptr.read(rec_len)
            s = rec_unpack(data)
            self.data.append([float (s[0]) / float(100/self.DepthResolution), float (s[1] / 10)])

        # read an empty byte
        self.fileptr.read(1)        

        # now read the footer
        self.ETX, self.checksum = readFooter(self.numberOfBytes, self.fileptr)


###############################################################################
class X_DEPTH:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'X'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""

    def read(self):        
        self.fileptr.seek(self.offset, 0)                
        rec_fmt = '=LBBHLL4Hf2Hf4B'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = s[5]/1000
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        
        self.Heading         = float (s[8] / 100)
        self.SoundSpeedAtTransducer = float (s[9] / 10)
        self.TransducerDepth        = s[10]
        self.NBeams                 = s[11]
        self.NValidDetections       = s[12]
        self.SamplingFrequency      = s[13]
        self.ScanningInfo           = s[14]
        self.spare1                 = s[15]
        self.spare2                 = s[16]
        self.spare3                 = s[17]

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

###############################################################################
    def encode(self):
        '''Encode a Depth XYZ datagram record'''

        header_fmt = '=LBBHLL4Hf2Hf4B'
        header_len = struct.calcsize(header_fmt)

        fullDatagram = bytearray()

        rec_fmt = '=fffHBBBbh'            
        rec_len = struct.calcsize(rec_fmt)
       
        footer_fmt = '=BBH'
        footer_len = struct.calcsize(footer_fmt)

        fullDatagramByteCount = header_len + (rec_len*self.NBeams) + footer_len

        # pack the header
        recordTime = int(dateToSecondsSinceMidnight(from_timestamp(self.Time))*1000)
        header = struct.pack(header_fmt, fullDatagramByteCount-4, self.STX, ord(self.typeOfDatagram), self.EMModel, self.RecordDate, recordTime, self.Counter, self.SerialNumber, int(self.Heading * 100), int(self.SoundSpeedAtTransducer * 10), self.TransducerDepth, self.NBeams, self.NValidDetections, self.SamplingFrequency, self.ScanningInfo, self.spare1, self.spare2, self.spare3)
        fullDatagram = fullDatagram + header

        # pack the beam summary info
        for i in range (self.NBeams):
            bodyRecord = struct.pack(rec_fmt, self.Depth[i], self.AcrossTrackDistance[i], self.AlongTrackDistance[i], self.DetectionWindowsLength[i], self.QualityFactor[i], int(self.BeamIncidenceAngleAdjustment[i]*10), self.DetectionInformation[i], self.RealtimeCleaningInformation[i], int(self.Reflectivity[i]*10), )
            fullDatagram = fullDatagram + bodyRecord

        # now pack the footer 
        systemDescriptor = 1
        ETX = 3
        checksum = 0
        footer = struct.pack('=BBH', systemDescriptor, ETX, checksum)
        fullDatagram = fullDatagram + footer

        return fullDatagram

###############################################################################
class Y_SEABEDIMAGE:
    def __init__(self, fileptr, numberOfBytes):
        self.typeOfDatagram = 'Y'
        self.offset = fileptr.tell()
        self.numberOfBytes = numberOfBytes
        self.fileptr = fileptr
        self.fileptr.seek(numberOfBytes, 1)
        self.data = ""
        self.ARC = {}
        self.BeamPointingAngle=[]

    def read(self):
        self.fileptr.seek(self.offset, 0)
        rec_fmt = '=LBBHLLHHfHhhHHH'
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack_from
        s = rec_unpack(self.fileptr.read(rec_len))

        # self.numberOfBytes   = s[0]
        self.STX             = s[1]
        self.typeOfDatagram  = chr(s[2])
        self.EMModel         = s[3]
        self.RecordDate      = s[4]
        self.Time            = float(s[5]/1000.0)
        self.Counter         = s[6]
        self.SerialNumber    = s[7]
        self.SampleFrequency   = s[8]
        self.RangeToNormalIncidence   = s[9]
        self.NormalIncidence   = s[10]
        self.ObliqueBS   = s[11]
        self.TxBeamWidth   = s[12]
        self.TVGCrossOver   = s[13]
        self.NumBeams   = s[14]
        self.beams = []
        self.numSamples = 0
        self.samples =[]

        rec_fmt = '=bBHH'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack

        self.numSamples = 0
        for i in range(self.NumBeams):            
            s = rec_unpack(self.fileptr.read(rec_len))
            b = cBeam(s, 0)
            self.numSamples = self.numSamples + b.numberOfSamplesPerBeam
            self.beams.append(b)

        rec_fmt = '=' + str(self.numSamples) + 'h'            
        rec_len = struct.calcsize(rec_fmt)
        rec_unpack = struct.Struct(rec_fmt).unpack
        self.samples = rec_unpack(self.fileptr.read(rec_len))
        
        # allocate the samples to the correct beams so it is easier to use
        sampleIDX = 0
        for b in self.beams:
            b.samples = self.samples[sampleIDX: sampleIDX + b.numberOfSamplesPerBeam] 
            sampleIDX = sampleIDX + b.numberOfSamplesPerBeam

        # read an empty byte
        self.fileptr.read(1)        

        # now read the footer
        self.ETX, self.checksum = readFooter(self.numberOfBytes, self.fileptr)

###############################################################################
    def encode(self):
        '''Encode a seabed image datagram record'''

        header_fmt = '=LBBHLLHHfHhhHHH'
        header_len = struct.calcsize(header_fmt)

        fullDatagram = bytearray()
        
        rec_fmt = '=bBHH'            
        rec_len = struct.calcsize(rec_fmt)

        sample_fmt = '=' + str(self.numSamples) + 'h'            
        sample_len = struct.calcsize(sample_fmt)
        
        footer_fmt = '=BBH'
        footer_len = struct.calcsize(footer_fmt)

        fullDatagramByteCount = header_len + (rec_len*self.NumBeams) + sample_len + footer_len

        # pack the header
        recordTime = int(dateToSecondsSinceMidnight(from_timestamp(self.Time))*1000)
        header = struct.pack(header_fmt, fullDatagramByteCount-4, self.STX, ord(self.typeOfDatagram), self.EMModel, self.RecordDate, recordTime, self.Counter, self.SerialNumber, self.SampleFrequency, self.RangeToNormalIncidence, self.NormalIncidence, self.ObliqueBS, self.TxBeamWidth, self.TVGCrossOver, self.NumBeams)
        fullDatagram = fullDatagram + header

        # pack the beam summary info
        s = []
        for i,b in enumerate (self.beams):
            bodyRecord = struct.pack(rec_fmt, b.sortingDirection, b.detectionInfo, b.numberOfSamplesPerBeam, b.centreSampleNumber)
            fullDatagram = fullDatagram + bodyRecord
            # using the takeoffangle, we need to look up the correction from the ARC and apply it to the samples.
            a = round(self.BeamPointingAngle[i],0)
            correction = self.ARC[a]
            for sample in b.samples:
                s.append(int(sample + correction))
        sampleRecord = struct.pack(sample_fmt, *s)
        fullDatagram = fullDatagram + sampleRecord

        # now pack the footer 
        systemDescriptor = 1
        ETX = 3
        checksum = 0
        footer = struct.pack('=BBH', systemDescriptor, ETX, checksum)
        fullDatagram = fullDatagram + footer

        return fullDatagram

###############################################################################
# TIME HELPER FUNCTIONS
###############################################################################
def to_timestamp(dateObject):
    return (dateObject - datetime(1970, 1, 1)).total_seconds()

def from_timestamp(unixtime):
    return datetime.utcfromtimestamp(unixtime)

def dateToKongsbergDate(dateObject):
    return dateObject.strftime('%Y%m%d')

def dateToKongsbergTime(dateObject):
    return dateObject.strftime('%H%M%S')

def dateToSecondsSinceMidnight(dateObject):
    return (dateObject - dateObject.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()

############################################################################### 
# bitwise helper functions
############################################################################### 
def isBitSet(int_type, offset):
    '''testBit() returns a nonzero result, 2**offset, if the bit at 'offset' is one.'''
    mask = 1 << offset
    return (int_type & (1 << offset)) != 0

def swap16(i):
    return struct.unpack("<H", struct.pack(">H", i))[0]

def typecasting(crc):
    msb = hex(crc >> 8)
    lsb = hex(crc & 0x00FF)
    return lsb + msb

def crc16(data: bytes):
    '''
    CRC-16-CCITT Algorithm
    '''
    data = bytearray(data)
    poly = 0x8408
    crc = 0xFFFF
    for b in data:
        cur_byte = b & 0xFF
        for _ in range(0, 8):
            if (crc & 0x0001) ^ (cur_byte & 0x0001):
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1

            cur_byte >>= 1
    crc = ~crc
    crc = (crc << 8) | ((crc >> 8) & 0xFF)
    return ctypes.c_ushort(crc).value

# #define POLY 0x8408
# unsigned short blkcrc(unsigned char *bufptr, /* message buffer */ unsigned long len /* number of bytes */ )
# {
# unsigned char i;
# unsigned short data;
# unsigned short crc = 0xffff;
# if (len == 0L) 
# {
#   return ~crc;
# }
# do 
# {
#   for (i=0, data = (unsigned short) (0xff & *bufptr++); i < 8; i++, data >>= 1) 
#   {
#       if ((crc & 0x0001) ^ (data & 0x0001)) 
#       {
#           crc = (crc >> 1) ^ POLY;
#       } 
#       else 
#       {
#           crc >>= 1;
#       }
#   }
# } while (--len);
# crc = ~crc;
# data = crc;
# crc = (crc << 8) | ((data >> 8) & 0xff);
# return crc;
# }

if __name__ == "__main__":
        main()

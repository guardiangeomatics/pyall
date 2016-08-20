#name:          pyXTF
#created:       May 2016
#by:            p.kennedy@fugro.com
#description:   python module to read an XTF sonar file
#notes:         See main at end of script for example how to use this
#based on XTF version 34 21/2/2012
#version 2.00

# See readme.md for details

import pprint
import struct
import os.path
from datetime import datetime
import geodetic
import numpy as np
import time

class XTFNAVIGATIONRECORD:
    def __init__(self, dateTime, pingNumber, sensorX, sensorY, sensorDepth, sensorAltitude, SensorHeading, sensorSpeed):
        self.dateTime = dateTime
        self.pingNumber = pingNumber
        self.sensorX = sensorX
        self.sensorY = sensorY
        self.sensorDepth = sensorDepth
        self.sensorAltitude = sensorAltitude
        self.sensorHeading = SensorHeading
        self.sensorSpeed = sensorSpeed
           
class XTFPINGHEADER:
    def __init__(self, fileptr, XTFFileHdr, SubChannelNumber, NumChansToFollow, NumBytesThisRecord):
        # start_time = time.time() # time the process

        data = fileptr.read(XTFFileHdr.XTFPingHeader_len)
        s = XTFFileHdr.XTFPingHeader_unpack(data)
        
        self.SubChannelNumber = SubChannelNumber #pass the parameter into the correct class
        self.Year                           = s[0]
        self.Month                          = s[1]
        self.Day                            = s[2]
        self.Hour                           = s[3]
        self.Minute                         = s[4]
        self.Second                         = s[5]
        self.HSeconds                       = s[6]
        self.JulianDays                     = s[7]
        self.EventNumber                    = s[8]
        self.PingNumber                     = s[9]
        self.SoundVelocity                  = s[10]
        self.OceanTide                      = s[11]
        self.Reserved2                      = s[12]
        self.ConductivityFreq               = s[13]
        self.TemperatureFreq                = s[14]
        self.PressureFreq                   = s[15]
        self.PressureTemp                   = s[16]
        self.Conductivity                   = s[17]
        self.WaterTemperature               = s[18]
        self.Pressure                       = s[19]
        self.ComputedSoundVelocity          = s[20]
        self.MagX                           = s[21]
        self.MagY                           = s[22]
        self.MagZ                           = s[23]
        self.AuxVal1                        = s[24]
        self.AuxVal2                        = s[25]
        self.AuxVal3                        = s[26]
        self.AuxVal4                        = s[27]
        self.AuxVal5                        = s[28]
        self.AuxVal6                        = s[29]
        self.SpeedLog                       = s[30]
        self.Turbidity                      = s[31]
        self.ShipSpeed                      = s[32]
        self.ShipGyro                       = s[33]
        self.ShipYcoordinate                = s[34]                        
        self.ShipXcoordinate                = s[35]
        self.ShipAltitiude                  = s[36]
        self.ShipDepth                      = s[37]
        self.FixTimeHour                    = s[38]
        self.FixTimeMinute                  = s[39]
        self.FixTimeSecond                  = s[40]
        self.FixTimeHsecond                 = s[41]
        self.SensorSpeed                    = s[42]
        self.KP                             = s[43]
        self.SensorYcoordinate              = s[44]
        self.SensorXcoordinate              = s[45]
        self.SonarStatus                    = s[46]
        self.RangeToTowFish                 = s[47]
        self.BearingToTowFish               = s[49]
        self.CableOut                       = s[49]
        self.Layback                        = s[50]
        self.CableTension                   = s[51]
        self.SensorDepth                    = s[52]
        self.SensorPrimaryAltitude          = s[53]
        self.SensorAuxAltitude              = s[54]
        self.SensorPitch                    = s[55]
        self.SensorRoll                     = s[56]
        self.SensorHeading                  = s[57]
        self.Heave                          = s[58]
        self.Yaw                            = s[59]
        self.AttitudeTimeTag                = s[60]
        self.DOT                            = s[61]
        self.NavFixMilliseconds             = s[62]
        self.ComputerClockHour              = s[63]
        self.ComputerClockMinute            = s[64]
        self.ComputerClockSecond            = s[65]
        self.ComputerClockHSecond           = s[66]
        self.FishPositionDeltaX             = s[67]
        self.FishPositionDeltaY             = s[68]
        self.FishPositionErrorCode          = s[69]
        self.OptionalOffset                 = s[70]
        self.ReservedSpace2_1               = s[71]
        self.ReservedSpace2_2               = s[72]
        self.ReservedSpace2_3               = s[73]
        self.ReservedSpace2_4               = s[74]
        self.ReservedSpace2_5               = s[75]
        self.ReservedSpace2_6               = s[76]
        # print("--- %s.sss header read duration ---" % (time.time() - start_time)) # print the processing time.

        # now read the chaninfo records.  This is more complex than it needs to be, but for now, read six channels
        # start_time = time.time() # time the process
        self.pingChannel =[]
        for i in range(NumChansToFollow):
            ping = XTFPINGCHANHEADER(fileptr, XTFFileHdr, i)
            self.pingChannel.append(ping)
        # print("--- %s.sss sample read duration ---" % (time.time() - start_time)) # print the processing time.

    def __str__(self):
        return (pprint.pformat(vars(self)))        
                
class XTFPINGCHANHEADER:
    def __init__(self, fileptr, XTFFileHdr, channelIndex):
        # print ("XTFPingChanHeader Length: ", XTFPingChanHeader_len)
        
        hdr = fileptr.read(XTFFileHdr.XTFPingChanHeader_len)
        s = XTFFileHdr.XTFPingChanHeader_unpack(hdr)
        self.ChannelNumber                    = s[0]
        self.DownsampleMethod                 = s[1]
        self.SlantRange                       = s[2]
        self.GroundRange                      = s[3]
        self.TimeDelay                        = s[4]
        self.TimeDuration                     = s[5]
        self.SecondsPerPing                   = s[6]
        self.ProcessingFlags                  = s[7]
        self.Frequency                        = s[8]
        self.InitialGainCode                  = s[9]
        self.GainCode                         = s[10]
        self.BandWidth                        = s[11]
        self.ContactNumber                    = s[12]
        self.ContactClassification            = s[13]
        self.ContactSubNumber                 = s[14]
        self.ContactType                      = s[15]
        self.NumSamples                       = s[16]
        self.MillivoltScale                   = s[17]
        self.ContactTimeOffTrack              = s[18]
        self.ContactCloseNumber               = s[19]
        self.Reserved2                        = s[20]
        self.FixedVSOP                        = s[21]
        self.Weight                           = s[22]
        self.ReservedSpace1                   = s[23]
        self.ReservedSpace2                   = s[24]
        self.ReservedSpace3                   = s[25]
        self.ReservedSpace4                   = s[26]

        if XTFFileHdr.XTFChanInfo[channelIndex].UniPolar == 0: #polar mean signed data
            if XTFFileHdr.XTFChanInfo[channelIndex].BytesPerSample == 1: #1 byte per sample
                XTFdata_fmt = '=' + str(self.NumSamples) + 'b'
            else:
                XTFdata_fmt = '=' + str(self.NumSamples) + 'h'                
        else: # we are using unipolar data
            if XTFFileHdr.XTFChanInfo[channelIndex].BytesPerSample == 1: #1 byte per sample
                XTFdata_fmt = '=' + str(self.NumSamples) + 'B'
            else:
                XTFdata_fmt = '=' + str(self.NumSamples) + 'H'                
            
        #now read the sonar data
        XTFdata_len = struct.calcsize(XTFdata_fmt)
        XTFdata_unpack = struct.Struct(XTFdata_fmt).unpack_from
        blob = fileptr.read(XTFdata_len)
        self.data = XTFdata_unpack(blob)
        # print ("XTFdata_len: ", XTFdata_len)
        
        return
        
    def __str__(self):
        return (pprint.pformat(vars(self)))        
        
class XTFCHANINFO:
    def __init__(self, fileptr, XTFFileHdr):

        data = fileptr.read(XTFFileHdr.XTFChanInfo_len)
        s = XTFFileHdr.XTFChanInfo_unpack(data)
        self.TypeOfChannel                    = s[0]
        self.SubChannelNumber                 = s[1]
        self.CorrectionFlags                  = s[2]
        self.UniPolar                         = s[3]
        self.BytesPerSample                   = s[4]
        self.Reserved                         = s[5]
        self.ChannelName                      = s[6].decode('utf-8').rstrip('\x00')
        self.VoltScale                        = s[7]
        self.Frequency                        = s[8]
        self.HorizBeamAngle                   = s[9]
        self.TiltAngle                        = s[10]
        self.BeamWidth                        = s[11]
        self.OffsetX                          = s[12]
        self.OffsetY                          = s[13]
        self.OffsetZ                          = s[14]
        self.OffsetYaw                        = s[15]
        self.OffsetPitch                      = s[16]
        self.OffsetRoll                       = s[17]
        self.BeamsPerArray                    = s[18]
        self.SampleFormat                     = s[19]
        self.ReservedArea2                    = s[20].decode('utf-8').rstrip('\x00')
                        
    def __str__(self):
        return (pprint.pformat(vars(self)))

class XTFFILEHDR:
    def __init__(self, fileptr):
        XTFFileHdr_fmt = '=bb8s8s16sh64s64s3hbbhbbHf12b10bl12f'
        XTFFileHdr_len = struct.calcsize(XTFFileHdr_fmt)
        XTFFileHdr_unpack = struct.Struct(XTFFileHdr_fmt).unpack_from
        # print ("XTFFILEINFO Length:", XTFFileHdr_len)

        #hold the formats in the file header class as we do not need to spend time creaitng them for ecery record.  That is too slow.
        XTFPingHeader_fmt = '=h6bh2L2fL21f2d2h4b2f2d4h10fLfL4b2hBL7b'
        self.XTFPingHeader_len = struct.calcsize(XTFPingHeader_fmt)
        self.XTFPingHeader_unpack = struct.Struct(XTFPingHeader_fmt).unpack_from

        XTFChanInfo_fmt = '=bb3hl16s11fhb53s'
        self.XTFChanInfo_len = struct.calcsize(XTFChanInfo_fmt)
        self.XTFChanInfo_unpack = struct.Struct(XTFChanInfo_fmt).unpack_from

        XTFPingChanHeader_fmt = '=2h5f5hLh2bLhf2bfh4b'
        self.XTFPingChanHeader_len = struct.calcsize(XTFPingChanHeader_fmt)
        self.XTFPingChanHeader_unpack = struct.Struct(XTFPingChanHeader_fmt).unpack_from

        data = fileptr.read(XTFFileHdr_len)
        s = XTFFileHdr_unpack(data)
        self.FileFormat                         = s[0]
        self.SystemType                         = s[1]
        self.RecordingProgramName               = s[2].decode('utf-8').rstrip('\x00')
        self.RecordingProgramVersion            = s[3].decode('utf-8').rstrip('\x00')
        self.SonarName                          = s[4].decode('utf-8').rstrip('\x00')
        self.SonarType                          = s[5]
        self.NoteString                         = s[6].decode('utf-8').rstrip('\x00')
        self.ThisFileName                       = s[7].decode('utf-8').rstrip('\x00')
        self.NavUnits                           = s[8]
        self.NumberOfSonarChannels              = s[9]
        self.NumberOfBathymetryChannels         = s[10]
        self.NumberOfSnippetChannels            = s[11]
        self.NumberOfForwardLookArrays          = s[12]
        self.NumberOfInterferometryChannels     = s[13]
        self.Reserved1                          = s[14]
        self.Reserved2                          = s[15]
        self.ReferencePointHeight               = s[16]
        self.ProjectionType                     = s[17]
        self.SpheroidType                       = s[18]
        self.NavigationLatency                  = s[19]
        self.OriginX                            = s[20]
        self.Originy                            = s[21]
        self.NavoffsetX                         = s[22]
        self.NavoffsetY                         = s[23]
        self.NavoffsetZ                         = s[24]
        self.NavoffsetYaw                       = s[25]
        self.NavoffsetX                         = s[26]
        self.MRUoffsetY                         = s[27]
        self.MRUoffsetZ                         = s[28]
        self.MRUoffsetYaw                       = s[29]
        self.MRUoffsetPitch                     = s[30]
        self.MRUoffsetRoll                      = s[31]

        # now read the chaninfo records.  This is more complex than it needs to be, but for now, read six channels
        self.XTFChanInfo =[]
        for i in range(6):
            ch = XTFCHANINFO(fileptr, self)
            self.XTFChanInfo.append(ch)
            
        # there can be more than 6 channels.  If so, we need to read another 1024 bytes here.  As we do not have an example of this, the code is not written
        
    def __str__(self):
        return (pprint.pformat(vars(self)))

class XTFReader:
    XTFPacketHeader_fmt = '=h2b3hL'
    XTFPacketHeader_len = struct.calcsize(XTFPacketHeader_fmt)
    XTFPacketHeader_unpack = struct.Struct(XTFPacketHeader_fmt).unpack_from

    def __init__(self, XTFfileName):
        if not os.path.isfile(XTFfileName):
            print ("file not found:", XTFfileName)
        self.fileName = XTFfileName
        self.fileptr = open(XTFfileName, 'rb')        
        self.fileSize = self.fileptr.seek(0, 2)
        # go back to start of file
        self.fileptr.seek(0, 0)                
        self.XTFFileHdr = XTFFILEHDR(self.fileptr)
            
    def __str__(self):
        return pprint.pformat(vars(self))

    def close(self):
        self.fileptr.close()
        
    def rewind(self):
        # go back to start of file
        self.fileptr.seek(0, 0)                
        self.XTFFileHdr = XTFFILEHDR(self.fileptr)
        
    def moreData(self):
        bytesRemaining = self.fileSize - self.fileptr.tell()
        # print ("current file ptr position:", self.fileptr.tell())
        return bytesRemaining
            
    def loadNavigation(self):
        navigation = []
        start_time = time.time() # time the process
        while self.moreData():
            pingHdr = self.readPacket()
            # we need to calculate the approximate speed, so need the ping interval
            d = datetime (pingHdr.Year, pingHdr.Month, pingHdr.Day, pingHdr.Hour, pingHdr.Minute, pingHdr.Second, pingHdr.HSeconds * 10000)
            r = XTFNAVIGATIONRECORD(d, pingHdr.PingNumber, pingHdr.SensorXcoordinate, pingHdr.SensorYcoordinate, pingHdr.SensorDepth, pingHdr.SensorPrimaryAltitude, pingHdr.SensorHeading, pingHdr.SensorSpeed)
            navigation.append(r)
            
        self.rewind()
        print("Get navigation Range Duration %.3fs" % (time.time() - start_time)) # print the processing time.
        return (navigation)
    
    def computeSpeedFromPositions(self, navData):
        if (navData[0].sensorX <= 180) & (navData[0].sensorY <= 90): #data is in geographicals
            for r in range(len(navData) - 1):
                rng, bearing12, bearing21 = geodetic.calculateRangeBearingFromGeographicals(navData[r].sensorX, navData[r].sensorY, navData[r+1].sensorX, navData[r+1].sensorY)               
                # now we have the range, comput the speed in metres/second. where speed = distance/time
                navData[r].sensorSpeed = rng / (navData[r+1].dateTime.timestamp() - navData[r].dateTime.timestamp())             
        else:
            for r in range(len(navData) - 1):
                rng, bearing12, bearing21 = geodetic.calculateRangeBearingFromGridPosition(navData[r].sensorX, navData[r].sensorY, navData[r+1].sensorX, navData[r+1].sensorY)               
                # now we have the range, comput the speed in metres/second. where speed = distance/time
                navData[r].sensorSpeed = rng / (navData[r+1].dateTime.timestamp() - navData[r].dateTime.timestamp())             
                
        # now smooth the sensorSpeed
        speeds = [o.sensorSpeed for o in navData]
        npspeeds=np.array(speeds)
        
        smoothSpeed = geodetic.medfilt(npspeeds, 5)
        meanSpeed = float(np.mean(smoothSpeed))
        
        for r in range(len(navData) - 1):
            navData[r].sensorSpeed = float (smoothSpeed[r])

        return meanSpeed, navData
          
    def readPacketheader(self):
        data = self.fileptr.read(self.XTFPacketHeader_len)
        s = self.XTFPacketHeader_unpack(data)

        MagicNumber                    = s[0]
        HeaderType                     = s[1]
        SubChannelNumber               = s[2]
        NumChansToFollow               = s[3]
        Reserved1                      = s[4]
        Reserved2                      = s[5]
        NumBytesThisRecord             = s[6]

        return HeaderType, SubChannelNumber, NumChansToFollow, NumBytesThisRecord

    def readPacket(self):
        ping = -999
        # remember the start position, so we can easily comput the position of the next packet
        currentPacketPosition = self.fileptr.tell()

        # read the packet header.  This permits us to skip packets we do not support
        HeaderType, SubChannelNumber, NumChansToFollow, NumBytesThisRecord = self.readPacketheader()
        if HeaderType == 0:
            ping = XTFPINGHEADER(self.fileptr, self.XTFFileHdr, SubChannelNumber, NumChansToFollow, NumBytesThisRecord)
            
            # now read the padbytes at the end of the packet
            padBytes = currentPacketPosition + NumBytesThisRecord - self.fileptr.tell()
            if padBytes > 0:
                data = self.fileptr.read(padBytes)
        else:
            print ("unsupported packet type: %s at byte offset %s" % (HeaderType, currentPacketPosition))
            self.fileptr.seek(currentPacketPosition + NumBytesThisRecord, 0)
    
        return ping
    
    # def readChannel(self):        
    #     return XTFPINGCHANHEADER()
         
if __name__ == "__main__":
    #open the XTF file for reading by creating a new XTFReader class and passin in the filename to open.  The reader will read the initial header so we can get to grips with the file contents with ease.  
    r = XTFReader("C:/development/python/ssl-0064-vsm3_17-20151122-175354_P_Rev2.xtf")
    # r = XTFReader("C:/development/python/ssh-0065-vsm3_16-20151122-182327_P_Rev2.xtf")
    
    # print the XTF file header information.  This gives a brief summary of the file contents.
    for ch in range(r.XTFFileHdr.NumberOfSonarChannels):
        print(r.XTFFileHdr.XTFChanInfo[ch])

    while r.moreData():
        pingHdr = r.readPacket()
        # print (pingHdr.PingNumber,  pingHdr.SensorXcoordinate, pingHdr.SensorYcoordinate)

    r.rewind()
    navigation = r.loadNavigation()
    for n in navigation:
        print ("X: %.3f Y: %.3f Hdg: %.3f Alt: %.3f Depth: %.3f" % (n.sensorX, n.sensorY, n.sensorHeading, n.sensorAltitude, n.sensorDepth))
    print("Complete reading XTF file :-)")
    r.close()    

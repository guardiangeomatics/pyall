pyall
=====
* created:       August 2016
* by:            p.kennedy@fugro.com
* description:   python module to read an XTF sonar file
* notes:         See main at end of script for example how to use this
* based on ALL file version 
* version 1.00
* developed for Python version 3.4 

Done
====

2Do
===
* everything 

Example Reader
-------
```
    # opening the file reads the header and then the channelinfo automatically
    r = ALLReader(<filename>)
        # we can then loop through all packets, which drills down into the sonar records through the xtfchaninfo, xtfchanheader to the actual sonar data 
        while r.moreData():
            pingHdr = r.readPing()
    # close the File 
    r.close()
    # see the test code in main() at the end of pyall for more details.  Have Fun
```
```
Data Type Conversions from ALL to Python::     
    * ALL types to python struct types
    * signed char = 1 byte = "b"
    * unsigned char = 1 byte = "B"
    * XTFWORD = signed int 2 bytes = h
    * XTFWORD = UNsigned int 2 bytes = H (for unipolar data)
    * DWORD = unsigned int 4 bytes = "L"
    * short = short integer 2 bytes = "h"
    * char = 1 byte = "c"
```
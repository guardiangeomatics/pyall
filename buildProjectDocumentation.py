#created p.kennedy@fugro.com
#created: May 2015
#Based on twitter bootstrap

import os
import sys
import re
import time
import datetime

# set an include path
sys.path.append("./_scripts") 
import zBMS
import scan	
import whatsNew

# import repairMenu
outputFileName = "index.html"
ignoreFolders = ['_parts', 'images', '_trash', '_bootstrap', '_scripts', '__pychache__', 'aspnet_client', '.vscode', '.git']

print("Starting to compile the Project Documentation...")
print("compiling static parts..")

projectconfig = scan.loadCSVFile('config.txt')

fin = open("./_parts/1head.html", "r")
document = fin.read()
fin.close()
fout = open(outputFileName, "w")
fout.write(document)
fout.close()

scan.mergeFile(outputFileName, "./_parts/2bodyStart.html")

# build the menu system
scan.mergeFile(outputFileName,"./_parts/34menuHeader.html")
scan.buildDropDownMenu("dropdownmenu.txt", "./", ignoreFolders)
scan.mergeFile(outputFileName, "dropdownmenu.txt")

scan.mergeFile(outputFileName,"./_parts/35menuSideBarHeader.html")
scan.buildSideBarMenu("sidebarmenu.txt", "./", ignoreFolders)
scan.mergeFile(outputFileName, "sidebarmenu.txt")

scan.mergeFile(outputFileName,"./_parts/5title.html")

#create the whatsnew section
whatsNew.whatsnew("tmp.txt", "./", ignoreFolders)

# scan folders and sub folders and build all links...
scan.scanFolders("tmp.txt", "./", ignoreFolders)

now = datetime.datetime.now()
compileStr = projectconfig['projectid'] + " Updated: " + now.strftime("%d/%m/%y %H:%M")
print(compileStr)
scan.wordSearchReplace(outputFileName, "compileInfo", compileStr )
scan.wordSearchReplace(outputFileName, "projectname", projectconfig['projectname'] )
scan.wordSearchReplace(outputFileName, "projectsummary", projectconfig['projectsummary'] )
scan.wordSearchReplace(outputFileName, "browsertabname", projectconfig['browsertabname'] )

scan.mergeFile(outputFileName,"tmp.txt")
os.remove("tmp.txt")

#Overview pages...
scan.mergeFile(outputFileName,"./_parts/about.html")
scan.mergeFile(outputFileName,"./_parts/contact.html")
scan.mergeFile(outputFileName,"./_parts/overview.html")

os.remove("dropdownmenu.txt")
os.remove("sidebarmenu.txt")

#readme section with 2 boxes
print("Adding readme...")
scan.mergeFile(outputFileName,"./_parts/readme.html")

print("Adding the closing tags to the page...")
scan.mergeFile(outputFileName,"./_parts/99lastPart.html")

# print("Zipping the entire Portal into a all-in-one so users can self serve...")
# zBMS.zipEntireBMS(".")

print("Complete;-)")

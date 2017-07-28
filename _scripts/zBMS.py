# created p.kennedy@fugro.com
# created: May 2015
# Zip the BMS into a single folder with full paths preserved.
# 
import os
import zipfile
import sys
import re

def zipdir(path, ziph):
	# ziph is zipfile handle
	ignoreFolders = ['ZippedBMS', '_scripts', '__pycache__']

	for root, dirs, files in os.walk(path):
		print ("zipping: " + root)
		if any(x in root for x in ignoreFolders):
			print("Skipping ignored folder: " + root)
		else:
			for file in files:
				if os.path.splitext(file)[1] == '.py':
					print("Skipping ignored file: " + file)
				else:
					ziph.write(os.path.join(root, file))		
		
def zipEntireBMS(path):
	destinationZip = "./ZippedBMS/All in One/Fugro-BMS.zip"
	if os.path.isfile(destinationZip):
		print ("deleting old zip file from bms...")
		os.remove(destinationZip)
	print ("creating new zip file of entire bms.  This will take a couple of  minutes to be patient.  Will notify you when complete...")
	zipf = zipfile.ZipFile(destinationZip, 'w')
	zipdir(path, zipf)
	zipf.close()
	print ("Completed making the zip version of the bms. All good.")
	return
	

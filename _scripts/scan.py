# created p.kennedy@fugro.com
# created: May 2015
# Based on twitter bootstrap
# 
import os
import sys
import re
import csv

# specify a list of folder names which will be skipped in the scanning process.  The list can be as long as you like.

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
	
def loadCSVFile(fileName):
	# 2do pkpk skip multiple commas in the text file.  we can only have 1 comma per line or the dict does not work
	with open(fileName, 'r') as f:
		reader = csv.reader(f, delimiter=',', quotechar='"')
		data = dict(reader)
	return data

def scanFolders(outputFileName, folder, ignoreFolders):
	print("scanning folders and sub folders and build all links...")
	dirs = os.listdir( folder )
	
	for folder in dirs:
		if os.path.isdir(folder):
			if any(x in folder for x in ignoreFolders):
				print("Skipping ignored folder: " + folder)
			else:
				# folder = folder.title()
				print("compiling folder: " + folder)
				FolderListing2Portal(outputFileName, folder)
	return

def buildDropDownMenu(outputFileName, folder, ignoreFolders):
	print("scanning folders and sub folders and build the menu...")
	dirs = os.listdir( folder )
	for folder in dirs:
		if os.path.isdir(folder):
			if any(x in folder for x in ignoreFolders):
				print("Skipping ignored folder: " + folder)
			else:
				# folder = folder.title()
				print("compiling menu from folder: " + folder)
				FolderListing2DropDownMenu(outputFileName, folder)
	#close out the menu
	fout = open(outputFileName, "a")
	fout.write("					</ul>\n")
	fout.write("				</div>\n")
	fout.write("			</div>\n")
	fout.write("		</nav>\n")
	fout.close()
	return
	
def buildSideBarMenu(outputFileName, folder, ignoreFolders):
	print("scanning folders and sub folders and build the menu...")
	dirs = os.listdir( folder )
	for folder in dirs:
		if os.path.isdir(folder):
			if any(x in folder for x in ignoreFolders):
				print("Skipping ignored folder: " + folder)
			else:
				# folder = folder.title()
				print("compiling menu from folder: " + folder)
				FolderListing2SideBarMenu(outputFileName, folder)
	#close out the menu
	fout = open(outputFileName, "a")
	fout.write("					</ul>\n")
	fout.write("				</div>\n")
	fout.write("			</div>\n")
	fout.write("		</div>\n")
	fout.close()
	return
    
def FolderListing2Portal(outputFileName, folderName ):
	import makeFileListingAsHTMLTable 
	document = makeFileListingAsHTMLTable.makeListing(folderName)
	fout = open(outputFileName, "a")
	fout.write(document)
	fout.close()
	return

def FolderListing2DropDownMenu(outputFileName, folderName ):
	import makeFileListingAsHTMLTable 
	document = makeFileListingAsHTMLTable.makeListing2DropDownMenu(folderName)
	fout = open(outputFileName, "a")
	fout.write(document)
	fout.close()
	return

def FolderListing2SideBarMenu(outputFileName, folderName ):
	import makeFileListingAsHTMLTable 
	document = makeFileListingAsHTMLTable.makeListing2SideBarMenu(folderName)
	fout = open(outputFileName, "a")
	fout.write(document)
	fout.close()
	return

def mergeFile(outputFileName, filename ):
	fin = open(filename, "r")
	document = fin.read()
	fin.close()
	fout = open(outputFileName, "a")
	fout.write(document)
	fout.close()
	return

#replace a word with the target word based on case insensitivity, ie replace word,WORD,WoRd with Word					
def wordSearchReplace (filename, searchWord, targetWord):
	f = open(filename,'r')
	filedata = f.read()
	f.close()

	print(("Search&Replacing:" + targetWord))
	pattern = re.compile(searchWord, re.IGNORECASE)
	newdata = pattern.sub(targetWord, filedata)
	
	f = open(filename,'w')
	f.write(newdata)
	f.close()
	return

	
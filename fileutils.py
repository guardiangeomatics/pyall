import sys
import os
import fnmatch
from glob import glob
import shutil

from ctypes import Structure, c_int32, c_uint64, sizeof, byref, windll

class MemoryStatusEx(Structure):
    _fields_ = [
        ('length', c_int32),
        ('memoryLoad', c_int32),
        ('totalPhys', c_uint64),
        ('availPhys', c_uint64),
        ('totalPageFile', c_uint64),
        ('availPageFile', c_uint64),
        ('totalVirtual', c_uint64),
        ('availVirtual', c_uint64),
        ('availExtendedVirtual', c_uint64)]
    def __init__(self):
        self.length = sizeof(self)

###############################################################################
def main(*opargs, **kwargs):
	'''test rig for fileutils'''

	filename= "c:/temp/pk_1.txt"
	f = open(filename, "w")
	f.write("gg")
	f.close()
	print(filename)
	filename = createOutputFileName(filename, ext="")
	print(filename)

	filename = createOutputFileName(filename, ext="")
	print(filename)

	filename = createOutputFileName(filename, ext="")
	print(filename)

	return


	recursive = False
	# local folder
	print ("11", findFiles2(recursive, ".", "*.py"))
	# absolute folder
	mypath = os.path.dirname(os.path.realpath(__file__))
	print ("22", mypath, findFiles2(recursive, mypath, "*.py"))

	# recursive local folder
	recursive = True
	print ("33",  mypath, findFiles2(recursive, ".", "*.py"))
	#recursive absolute folder
	mypath = os.path.dirname(os.path.realpath(__file__))
	print ("44",  mypath, findFiles2(recursive, mypath, "*.py"))




###############################################################################
def createOutputFileName(path, ext=""):
	'''Create a valid output filename. if the name of the file already exists the file name is auto-incremented.'''
	path = os.path.expanduser(path)
	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))

	if not os.path.exists(path):
		return path

	if len(ext) == 0:
		root, ext = os.path.splitext(os.path.expanduser(path))
	else:
		# use the user supplied extension
		root, ext2 = os.path.splitext(os.path.expanduser(path))

	dir		= os.path.dirname(root)
	fname	= os.path.basename(root)
	candidate = fname+ext
	index	= 1
	ls		= set(os.listdir(dir))
	candidate = "{}_{}{}".format(fname,index,ext)
	while candidate in ls:
			candidate = "{}_{}{}".format(fname,index,ext)
			index	+= 1

	return os.path.join(dir, candidate).replace('\\','/')

###############################################################################

# ###############################################################################
# def createOutputFileName(path):
# 	'''Create a valid output filename. if the name of the file already exists the file name is auto-incremented.'''
# 	path	  = os.path.expanduser(path)

# 	if not os.path.exists(os.path.dirname(path)):
# 		os.makedirs(os.path.dirname(path))

# 	if not os.path.exists(path):
# 		return path

# 	root, ext = os.path.splitext(os.path.expanduser(path))
# 	dir	   = os.path.dirname(root)
# 	fname	 = os.path.basename(root)
# 	candidate = fname+ext
# 	index	 = 1
# 	ls		= set(os.listdir(dir))
# 	while candidate in ls:
# 			candidate = "{}_{}{}".format(fname,index,ext)
# 			index	+= 1
# 	return os.path.join(dir, candidate)

###############################################################################
def findFiles2(recursive, filespec, filter):
	'''tool to find files based on user request.  This can be a single file, a folder start point for recursive search or a wild card'''
	matches = []
	if recursive:
		matches = glob(os.path.join(filespec, "**", filter), recursive = True)
	else:
		matches = glob(os.path.join(filespec, filter))
	
	mclean = []
	for m in matches:
		mclean.append(m.replace('\\','/'))
		
	# if len(mclean) == 0:
	# 	print ("Nothing found to convert, quitting")
		# exit()
	return mclean
###############################################################################
def findFiles(recursive, filespec, filter):
	'''tool to find files based on user request.  This can be a single file, a folder start point for recursive search or a wild card'''
	filespec = filespec + "/"
	matches = []
	if recursive:
		if not os.path.exists(filespec):
			#if the user passes a relative path, deal with it
			filespec = os.path.join(os.getcwd(), filespec)
		for root, dirnames, filenames in os.walk(os.path.dirname(filespec)):
			for f in fnmatch.filter(filenames, filter):
				matches.append(os.path.join(root, f))
				print (matches[-1])
	else:
		if os.path.exists(filespec):
			matches.append (os.path.abspath(filespec))
		else:
			for filename in glob(filespec):
				matches.append(filename)
	if len(matches) == 0:
		print ("Nothing found to convert, quitting")
		return []
	print ("File Find Count:", len(matches))
	return matches

###############################################################################
def addFileNameAppendage(path, appendage):
	'''Create a valid output filename. if the name of the file already exists the file name is auto-incremented.'''
	path = os.path.expanduser(path)

	if not os.path.exists(os.path.dirname(path)):
		os.makedirs(os.path.dirname(path))

	# if not os.path.exists(path):
	# 	return path

	root, ext = os.path.splitext(os.path.expanduser(path))
	dir	   = os.path.dirname(root)
	fname	 = os.path.basename(root)
	candidate = "{}{}{}".format(fname, appendage, ext)

	return os.path.join(dir, candidate)

###############################################################################
def copyfile(srcfile, dstfile, replace=True):
	'''Copy a file safely'''	
	
	# log ("Copying %s to %s" %(srcfile, dstfile))

	if not os.path.exists(srcfile):
		print ("source file does not exist, skipping : %s" % (srcfile))
		return 0, ""

	if os.path.isfile(dstfile) and replace:
		# Handle errors while calling os.remove()
		try:
			os.remove(dstfile)
		except:			
			print("Error while deleting file %s. Maybe its in use?" % (dstfile))

		# Handle errors while calling os.ulink()
		try:
			os.ulink(dstfile)
		except:
			print("Error while deleting file %s. Maybe its in use?" % (dstfile))

	if os.path.exists(dstfile):
		print ("destination file exists, skipping : %s" % (dstfile))
		return 0 , dstfile

	# the file does not exist so copy it.
	try:
		shutil.copy(srcfile, dstfile)
		return 1, dstfile
	except:
		print("Error while copying file %s" % (dstfile))
		return 0, ""

###############################################################################
def outfilename(filename, prefix="", appendix="", extension=""):
	filename = filename.replace('\\','/')
	root, ext = os.path.splitext(os.path.basename(filename))
	if len(extension) == 0:
		extension = ext
	if not "." in extension[0]:
		extension = "." + extension
	return os.path.join(os.path.dirname(filename), prefix + root + appendix + extension).replace('\\','/')

###############################################################################
def deletefile(filename):
	if os.path.exists(filename):
		try:			
			os.remove(filename)
		except:	
			return
			#log("file is locked, cannot delete: %s " % (filename))

###############################################################################
if __name__ == "__main__":
	print(outfilename("c:\\temp\\pk.txt", ))
	print(outfilename("c:/temp/pk.txt", "", "_appendix"))
	print(outfilename("c:/temp/pk.txt", "prefix_", "_appendix"))
	print(outfilename("c:/temp/pk.txt", "prefix_", "_appendix", "shp"))
	#main()

#name:		  	all2points
#created:		October 2023
#by:			paul.kennedy@guardiangeomatics.com
#description:   python module to read a Kongsberg ALL file, create a point cloud

#done##########################################

#todo##########################################

import os.path
from argparse import ArgumentParser
from datetime import datetime, timedelta
import math
import numpy as np
# import open3d as o3d
import sys
import time
import rasterio
import multiprocessing as mp
import shapefile
import logging

import pyall
import fileutils
import geodetic
import multiprocesshelper 
import cloud2tif
import lashelper
import ggmbesstandard

###########################################################################
def main():

	iho = ggmbesstandard.sp44()
	msg = str(iho.getordernames())

	parser = ArgumentParser(description='Read a ALL file and create point clouds.')
	parser.add_argument('-epsg', 	action='store', 		default="0",	dest='epsg', 			help='Specify an output EPSG code for transforming from WGS84 to East,North,e.g. -epsg 4326')
	parser.add_argument('-i', 		action='store',			default="", 	dest='inputfolder', 		help='Input filename/folder to process.')
	parser.add_argument('-cpu', 	action='store', 		default='0', 	dest='cpu', 			help='number of cpu processes to use in parallel. [Default: 0, all cpu]')
	parser.add_argument('-odir', 	action='store', 		default="",	dest='odir', 			help='Specify a relative output folder e.g. -odir GIS')
	parser.add_argument('-debug', 	action='store', 		default="500",	dest='debug', 			help='Specify the number of pings to process.  good only for debugging. [Default:-1]')
	parser.add_argument('-tvu', 	action='store_true', 		default=False,	dest='tvu', 			help='Use the Total Vertical Uncertainty cleaning algorithm')
	parser.add_argument('-verbose', 	action='store_true', 	default=False,		dest='verbose',			help='verbose to write LAZ files and other supproting file.s  takes some additional time!,e.g. -verbose [Default:false]')
	parser.add_argument('-standard',action='store', 		default="order1a",	dest='standard',		help='(optional) Specify the IHO SP44 survey order so we can set the filters to match the required specification. Select from :' + ''.join(msg) + ' [Default:order1a]' )
	parser.add_argument('-near', 	action='store', 		default="7",		dest='near',			help='(optional) ADVANCED:Specify the MEDIAN filter kernel width for computation of the regional surface so nearest neighbours can be calculated. [Default:5]')

	matches = []
	args = parser.parse_args()
	# args.inputfolder = "C:/sampledata/all/B_S2980_3005_20220220_084910.all"
	args.inputfolder = r"C:\sampledata\all\ncei_order_2023-10-09T06_31_19.276Z\multibeam-item-517619\insitu_ocean\trackline\atlantis\at26-15\multibeam\data\version1\MB\em122\0000_20140521_235308_Atlantis.all.mb58\0000_20140521_235308_Atlantis.all" 

	args.spherical = False
	args.tvu = True
	# args.verbose = True	

	if os.path.isfile(args.inputfolder):
		matches.append(args.inputfolder)

	if len (args.inputfolder) == 0:
		# no file is specified, so look for a .pos file in the current folder.
		inputfolder = os.getcwd()
		matches = fileutils.findFiles2(False, inputfolder, "*.all")

	if os.path.isdir(args.inputfolder):
		matches = fileutils.findFiles2(False, args.inputfolder, "*.all")

	#make sure we have a folder to write to
	args.inputfolder = os.path.dirname(matches[0])

	#make an output folder
	if len(args.odir) == 0:
		args.odir = os.path.join(args.inputfolder, str("GGOutlier_%s" % (time.strftime("%Y%m%d-%H%M%S"))))
	makedirs(args.odir)

	logging.basicConfig(filename = os.path.join(args.odir,"allclean_log.txt"), level=logging.INFO)
	log("configuration: %s" % (str(args)))
	log("Output Folder: %s" % (args.odir))

	results = []
	if args.cpu == '1':
		for file in matches:
			allcleaner(file, args)
	else:
		multiprocesshelper.log("Files to Import: %d" %(len(matches)))		
		cpu = multiprocesshelper.getcpucount(args.cpu)
		log("Processing with %d CPU's" % (cpu))

		pool = mp.Pool(cpu)
		multiprocesshelper.g_procprogress.setmaximum(len(matches))
		poolresults = [pool.apply_async(allcleaner, (file, args), callback=multiprocesshelper.mpresult) for file in matches]
		pool.close()
		pool.join()
		# for idx, result in enumerate (poolresults):
		# 	results.append([file, result._value])
		# 	print (result._value)

############################################################
def allcleaner(filename, args):
	'''we will try to auto clean beams by extracting the beam xyzF flag data and attempt to clean in scipy'''
	'''we then set the beam flags to reject files we think are outliers and write the all file to a new file'''

	#load the python proj projection object library if the user has requested it
	if args.epsg != "0":
		geo = geodetic.geodesy(args.epsg)
	else:
		args.epsg = pyall.getsuitableepsg(filename)
		geo = geodetic.geodesy(args.epsg)

	log("Processing file: %s" % (filename))

	maxpings = int(args.debug)
	if maxpings == -1:
		maxpings = 999999999

	pingcounter = 0
	beamcountarray = 0
	
	log("Loading Point Cloud...")
	pointcloud = pyall.loaddata(filename, args)
	xyz = np.column_stack([pointcloud.xarr, pointcloud.yarr, pointcloud.zarr, pointcloud.qarr, pointcloud.idarr])

	if args.verbose:
		#report on RAW POINTS
		outfile = os.path.join(args.odir, os.path.basename(filename) + "_R.txt")
		# xyz[:,2] /= ZSCALE
		np.savetxt(outfile, xyz, fmt='%.2f, %.3f, %.4f', delimiter=',', newline='\n')
		fname = lashelper.txt2las(outfile)
		#save as a tif file...
		outfilename = os.path.join(outfile + "_depth.tif")
		lashelper.lasgrid4( fname, outfilename, resolution=1, epsg=args.epsg)
		fileutils.deletefile(outfile)
		log ("Created LAZ file of input raw points: %s " % (fname))
		outfilename = os.path.join(outfile + "_Raw_depth.tif")
		# raw = np.asarray(pcd.points)
		# raw[:,2] /= ZSCALE
		# cloud2tif.saveastif(outfilename, geo, raw, fill=False)
		# outfilename = os.path.join(outfile + "_R_NEW.tif")
		# cloud2tif.pcd2meantif2(outfilename, geo, raw, fill=False)

	log("Cleaning complete at: %s" % (datetime.now()))
	return outfilename

###############################################################################
def update_progress(job_title, progress):
	'''progress value should be a value between 0 and 1'''
	length = 20 # modify this to change the length
	block = int(round(length*progress))
	msg = "\r{0}: [{1}] {2}%".format(job_title, "#"*block + "-"*(length-block), round(progress*100, 2))
	if progress >= 1: msg += " DONE\r\n"
	sys.stdout.write(msg)
	sys.stdout.flush()

###############################################################################
def	makedirs(odir):
	if not os.path.isdir(odir):
		os.makedirs(odir, exist_ok=True)

###############################################################################
def	log(msg, error = False, printmsg=True):
		if printmsg:
			print (msg)
		if error == False:
			logging.info(msg)
		else:
			logging.error(msg)

###############################################################################
if __name__ == "__main__":
		main()

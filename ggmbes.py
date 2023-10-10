#name:			ggmbes
#created:		July 2017
#by:			p.kennedy@guardiangeomatics.com
#description:	python module to represent MBES data so we can QC, compute and merge.
 
import pprint

###############################################################################
class GGPING:
	'''used to hold the metadata associated with a ping of data.'''
	def __init__(self):
		self.timestamp			= 0
		self.longitude 			= 0
		self.latitude 			= 0
		self.ellipsoidalheight 	= 0
		self.heading		 	= 0
		self.pitch			 	= 0
		self.roll			 	= 0
		self.heave			 	= 0
		self.tidecorrector	 	= 0
		self.hydroid		 	= 0
		self.hydroidsmooth	 	= 0
		self.waterLevelReRefPoint_m = 0
		self.txtransducerdepth_m = 0
		self.hydroidstandarddeviation = 0
	
	###############################################################################
	def __str__(self):
		return pprint.pformat(vars(self))


###############################################################################
class GGBeam:
	def __init__(self):
			self.east							= 0
			self.north							= 0
			self.depth 							= 0
			self.backscatter					= 0
			self.id 							= 0
			self.rejectionInfo1					= 0

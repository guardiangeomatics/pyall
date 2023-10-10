import os
import numpy as np
import math

###############################################################################
class ctimeSeries:
	'''# how to use the time series class, a 2D list of time
	# attitude = [[1,100],[2,200], [5,500], [10,1000]]
	# tsRoll = ctimeSeries(attitude)
	# print(tsRoll.getValueAt(6))'''


###############################################################################
	def __init__(self, timeOrtimeValue, values=""):
		'''the time series requires a 2d series of [[timestamp, value],[timestamp, value]].  It then converts this into a numpy array ready for fast interpolation'''
		self.name = "2D time series"
		# user has passed 1 list with both time and values, so handle it
		if len(values) == 0:
				if isinstance(timeOrtimeValue, np.ndarray):
					arr = timeOrtimeValue
				else:
					arr = np.array(timeOrtimeValue)
				#sort the list into ascending time order
				arr = arr[np.argsort(arr[:,0])]
				self.times = arr[:,0]
				self.values = arr[:,1]
		else:
			# user has passed 2 list with time and values, so handle it.  in this case the list MUST be sorted
			self.times = np.array(timeOrtimeValue)
			self.values = np.array(values)

###############################################################################
	def getValueAt(self, timestamp):
		'''get an interpolated value for an exact time'''
		'''requested values for times BEFORE the'''
		return np.interp(timestamp, self.times, self.values, left=None, right=None)

###############################################################################
	def getNearestAt(self, timestamp):
		'''get the nearest actual value to the time provided'''
		idx = np.searchsorted(self.times, timestamp, side="left")
		if idx > 0 and (idx == len(self.times) or math.fabs(timestamp - self.times[idx-1]) < math.fabs(timestamp - self.times[idx])):
			return self.times[idx-1], self.values[idx-1]
		else:
			return self.times[idx], self.values[idx]


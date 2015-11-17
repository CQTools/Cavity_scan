# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 11:41:56 2015

@author: Nick Lewty
"""

import timestampcontrol as tsc
from CQTdevices import DDSComm
import numpy as np
import matplotlib.pylab as plt
import time

# location of devices
DDS_address = '/dev/ioboards/DDS#'
DDS_channel = 0


#Connect to devices and create objects

#DDS = DDSComm(DDS_address,DDS_channel)

#Frequency range to scan in MHz
freq_point = 150

#Optical power from AOM in mW
power_set = 0.01

cal_data = np.genfromtxt('power_calibration.txt')


def power_convertion(freq_point,power_set,cal_data):#Converts set power to ampunits at specific frequency
	convertion_factor = 1000#May have to change this offten if input power to AOM changes
	xdata = cal_data[:,0]
	ydata = cal_data[:,1]
	i = np.where(xdata==(float(freq_point)))
	power_cal_factor = 1/(ydata[i]/np.max(ydata))
	ampunits = int(convertion_factor*power_cal_factor)
	if ampunits > 1024:
		print 'Maximium DDS power reached'
		ampunits = 1024
	elif ampunits < 2:
		print 'Minimium DDS power reached'
		ampunits = 1
	else:
		ampunits = ampunits
	return ampunits
#experiment procedure

power = power_convertion(freq_point,power_set,cal_data)
print power
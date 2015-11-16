# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 15:41:43 2015

@author: Nick Lewty
"""

from CQTdevices import DDSComm, PowerMeterComm
import matplotlib.pylab as plt
import numpy as np
import time



# location of devices
Power_meter_address = '/dev/serial/by-id/usb-Centre_for_Quantum_Technologies_Optical_Power_Meter_OPM-QO01-if00'

DDS_address = '/dev/ioboards/DDS#'
DDS_channel = 0

#Connect to devices and create objects
pm = PowerMeterComm(Power_meter_address)

#DDS = DDSComm(DDS_address,DDS_channel)

#Frequency range to scan in MHz
start = 150
stop = 250
step = 1

freq_range = np.arange(start,stop,step)


def power_scan(freq_range,average=10,wavelength=780):
	powers = []
	for i in freq_range:
		#DDS.set_freq(freq_range,'mhz')#set freq point
		value = []
		for i in range(average):
			power = pm.get_power(wavelength)
			value.append(power)
			time.sleep(5e-3) # delay between asking for next value
		powers.append(np.mean(value)) #average value to get more reliable number
	return np.array(powers)



#Calibration procedure

pm.set_range(4) # set suitable range for optical power being measured
#DDS.set_power(20,'ampunits')# set starting power make it low to ensure have enough adjustment when far from AOM resonance
powers = power_scan(freq_range) #run scan should take about a minute with 10 averages

plt.plot(freq_range,powers*1000.0)#plot data to make sure it makes sense
plt.xlabel('Frequency (MHz)')
plt.ylabel('Power (mW)')
plt.show()
data = np.column_stack((freq_range,powers))
np.savetxt('power_calibration.txt',data)
	
	
		



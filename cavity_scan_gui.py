#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:45:23 2015

@author: nick
"""

import sys


import time
import glob
import serial
import numpy as np
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QThread, QObject, pyqtSignal
import pyqtgraph as pg
import CQTdevices as dv
 


form_class = uic.loadUiType("cavityscangui.ui")[0] 

def serial_ports(value):
    
	"""Lists serial ports
	:raises EnvironmentError:
	On unsupported or unknown platforms
	:returns:
	A list of available serial ports
	"""				
	if sys.platform.startswith('win'):
		ports = ['COM' + str(i + 1) for i in range(256)]
	elif sys.platform.startswith('linux'):
	# this is to exclude your current terminal "/dev/tty"
		if value == 'freq':
			ports = glob.glob('/dev/serial/by-id/usb-W*')
		elif value == 'detector':
			ports = glob.glob('/dev/serial/by-id/usb-C*')
	elif sys.platform.startswith('darwin'):
		ports = glob.glob('/dev/tty.*')
	
	else:
		raise EnvironmentError('Unsupported platform')
	
	result = []
	for port in ports:
		try:
			s = serial.Serial(port)
			s.close()
			result.append(port)
		except serial.SerialException:
			pass
	return result


class ScanRunner(QObject):
	running = bool(False)
	finished = pyqtSignal()
	plotUpdate = pyqtSignal(list)
	freqIncreased = pyqtSignal(str, name = 'freqIncreased')
	stepIncreased = pyqtSignal(str, name = 'stepIncreased')
	devicestatus = pyqtSignal(str,name = 'devicestatus')
	def __init__(self,data,freq_device,detector_device, parent = None):
		super(ScanRunner, self).__init__()
		self.data = data
		self.windfreak = dv.windfreakusb2(freq_device)
		self.freq = float(self.windfreak.get_freq())/1000
		self.windfreak.set_clock(str(1))
		self.windfreak.set_freq(str(self.freq))
		time.sleep(0.2)
		self.detector = dv.Anlogcomm(detector_device)
		


	def run(self):
		self.running = True
		self.devicestatus.emit('connected')
		self.start_freq = self.data[0]
		self.stop_freq = self.data[1]
		self.step_freq = self.data[2]
		self.freq_range = np.arange(self.start_freq,self.stop_freq+self.step_freq,self.step_freq)
		self.amp_samples = []
		self.freqdata = []
		for i in range(len(self.freq_range)):
			if self.running:
				current_freq = self.freq_range[i]
				self.windfreak.set_freq(current_freq)
				time.sleep(0.2)
				read_freq = float(self.windfreak.get_freq())/1000
				time.sleep(0.2)
				read_detector = float(self.detector.get_voltage(1))
				self.freqIncreased.emit(str(read_freq)+' MHz')
				self.stepIncreased.emit(str(i))
				self.amp_samples.append(read_detector)
				self.freqdata.append(read_freq)
				time.sleep(0.2)
				self.plotUpdate.emit([self.freqdata,self.amp_samples])
		self.finished.emit()
		self.windfreak.close()
		self.detector.close()
		self.devicestatus.emit('Not connected')


	def stop(self):
		self.running = False
		print 'Stop'



class MyWindowClass(QtGui.QMainWindow, form_class):




	
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.StartButton.clicked.connect(self.ButtonUpdate_start_clicked)# Bind the event handlers
		self.comboSerialBox.addItems(serial_ports('freq')) #Gets a list of avaliable serial ports to connect to and adds to combo box
		self.comboSerialBox_2.addItems(serial_ports('detector'))
		self.StopButton.clicked.connect(self.ButtonUpdate_stop_clicked)
		self.pen = pg.mkPen(color=(0,0,0), width=2)
		self.plotWidget.plotItem.getAxis('left').setPen(self.pen)
		self.plotWidget.plotItem.getAxis('bottom').setPen(self.pen)
		self.plotWidget.setLabel('left', 'Amp', 'arb')
		self.plotWidget.setLabel('bottom', 'Freq', 'MHz')
		self.plt = self.plotWidget



			
	
	def ButtonUpdate_start_clicked(self):
		self.ScanThread = QThread(self)
		self.scandata = [float(self.StartSpinBox.text()),float(self.StopSpinBox.text()),float(self.StepSpinBox.text())]
		self.freq_device = str(self.comboSerialBox.currentText())
		self.detector_device = str(self.comboSerialBox_2.currentText())
		self.ScanRunner = ScanRunner(self.scandata,self.freq_device,self.detector_device)
		self.ScanRunner.devicestatus.connect(self.control_label.setText)
		self.ScanRunner.moveToThread(self.ScanThread)
		self.ScanThread.started.connect(self.ScanRunner.run)
		self.ScanRunner.freqIncreased.connect(self.label_Freq.setText)
		self.ScanRunner.stepIncreased.connect(self.label_Step.setText)
		self.ScanRunner.devicestatus.connect(self.control_label_2.setText)
		self.ScanRunner.plotUpdate.connect(self.update_plot)
		self.ScanThread.finished.connect(self.ScanThread.quit)
		self.ScanThread.start()
		
	def ButtonUpdate_stop_clicked(self):
		self.ScanRunner.stop()

		
	def update_plot(self,data):
		self.plt.plot(data[0],data[1],clear=True,pen={'color':'k','width':2})

		
		
		

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()

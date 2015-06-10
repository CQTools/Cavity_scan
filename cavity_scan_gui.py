#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 16:45:23 2015

@author: nick
"""

import sys
sys.path.append('../windfreak-pycontol')

import time
import glob
import serial
import numpy as np
from PyQt4 import QtGui, uic
from PyQt4.QtCore import QTimer, QThread, QObject, pyqtSignal
import pyqtgraph as pg
import windfreak_control2 as wc
 


form_class = uic.loadUiType("cavityscangui.ui")[0] 

def serial_ports():
    
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
		ports = glob.glob('/dev/serial/by-id/usb-W*')
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
	def __init__(self,data,freq_device, parent = None):
		super(ScanRunner, self).__init__()
		self.data = data
		self.windfreak = wc.windfreakusb2(freq_device)
		self.freq = float(self.windfreak.get_freq())/1000
		self.windfreak.set_clock(str(1))
		self.windfreak.set_freq(str(self.freq))
		time.sleep(1)
		#print self.data


	def run(self):
		self.running = True
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
				time.sleep(0.25)
				read_freq = float(self.windfreak.get_freq())/1000
				print read_freq
				self.freqIncreased.emit(str(read_freq)+' MHz')
				self.stepIncreased.emit(str(i))
				self.amp_samples.append(1)
				self.freqdata.append(read_freq)
				time.sleep(0.25)
				self.plotUpdate.emit(self.freqdata)
		self.finished.emit()

	def stop(self):
		self.running = False
		print 'Stop'



class MyWindowClass(QtGui.QMainWindow, form_class):
	connected = bool(False)
	windfreak = None
	scan = bool(False) 
	freqstart = pyqtSignal(float, name = 'freqstart')
	freqstop = pyqtSignal(float, name = 'freqstop')
	freqstep = pyqtSignal(float, name = 'freqstep')


	
	def __init__(self, parent=None):
		QtGui.QMainWindow.__init__(self, parent)
		self.setupUi(self)
		self.StartButton.clicked.connect(self.ButtonUpdate_start_clicked)# Bind the event handlers
		self.comboSerialBox.addItems(serial_ports()) #Gets a list of avaliable serial ports to connect to and adds to combo box
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
		self.ScanRunner = ScanRunner(self.scandata,self.freq_device)
		self.ScanRunner.moveToThread(self.ScanThread)
		self.ScanThread.started.connect(self.ScanRunner.run)
		self.ScanRunner.freqIncreased.connect(self.label_Freq.setText)
		self.ScanRunner.stepIncreased.connect(self.label_Step.setText)
		self.ScanRunner.plotUpdate.connect(self.update_plot)
		self.ScanThread.finished.connect(self.ScanThread.quit)
		self.ScanThread.start()
		
	def ButtonUpdate_stop_clicked(self):
		self.ScanRunner.stop()

		
	def update_plot(self,data):
		print data
		self.plt.plot(data,data,clear=True,pen={'color':'k','width':2})
#		except:
#			pass
		
		
		

app = QtGui.QApplication(sys.argv)
myWindow = MyWindowClass(None)
myWindow.show()
app.exec_()

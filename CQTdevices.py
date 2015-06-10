# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 15:13:21 2015

@author: nick
"""

import serial

class windfreakusb2(object):
	baudrate = 115200
		
	def __init__(self, port):
		self.serial = self._open_port(port)
		self._serial_write('+\n')# flush io buffer
		print self._serial_read() #will read unknown command
		
		
	def _open_port(self, port):
		ser = serial.Serial(port, self.baudrate, timeout=1)
		ser.readline()
		ser.timeout = 1
		return ser
		
	def _serial_write(self, string):
		self.serial.write(string + '\n')
		
	def _serial_read(self):
		msg_string = self.serial.readline()
		# Remove any linefeeds etc
		msg_string = msg_string.rstrip()
		return msg_string
		
	def get_freq(self):
		self._serial_write('f?')
		return self._serial_read()
	
	def rf_on(self):
		self._serial_write('o1')
		return self._serial_read()
	
	def rf_off(self):
		self._serial_write('o0')
		return self._serial_read()
	
	def rf_power_low(self):
		self._serial_write('h0')
	
	def rf_power_high(self):
		self._serial_write('h1')
	
	def set_pulse_mode(self,value):
		self._serial_write('j' + str(value))
	
	def get_pulse_mode(self,value):
		self._serial_write('j?')
		return self._serial_read()
		
	def get_power(self):
		self._serial_write('a?')
		return self._serial_read()
		
	def set_freq(self,value):
		self._serial_write('f' + str(value))
		return self._serial_read()
		
	def check_osci(self):
		self._serial_write('p')
		return self._serial_read()
	
	def set_clock(self,value):
		self._serial_write('x' + str(value))
		return self._serial_read()
	
	def get_clock(self):
		self._serial_write('x?')
		return self._serial_read()
	
	def set_power(self,value):
		self._serial_write('a' + str(value))
		return self._serial_read()
	
	def serial_number(self):
		self._serial_write('+')
		return self._serial_read()
		
	def close(self):
		self.serial.close()
		
class Anlogcomm(object):
# Module for communicating with the mini usb IO board
	baudrate = 115200
	def __init__(self, port):
		self.serial = self._open_port(port)
		self._serial_write('*IDN?')# flush io buffer
		print self._serial_read() #will read a command
		
    
	def _open_port(self, port):
		ser = serial.Serial(port, timeout=0.5)
		ser.readline()
		ser.timeout = 0.5 
		return ser
    
	def _serial_write(self, string):
		self.serial.write(string + '\n')
    
	def _serial_read(self):
		msg_string = self.serial.readline()
		# Remove any linefeeds etc
		msg_string = msg_string.rstrip()
		return msg_string
    
	def reset(self):
		self._serial_write('*RST')
		return self._serial_read()
        
	def get_voltage(self,channel):
		self._serial_write('IN?' + str(channel))
		voltage = self._serial_read()
		return voltage
        
	def get_voltage_all(self):
		self._serial_write('ALLIN?')
		allin = self._serial_read()
		return allin
    
    
	def set_voltage(self,channel,value):
		self._serial_write('OUT'+ str(channel) + str(value))
		return 
    
	def set_digitout(self,value):
		self._serial_write('DIGOUT' + str(value))
		return
    
	def close(self): 
		self.serial.close()

	def serial_number(self):
		self._serial_write('*IDN?')
		return self._serial_read()
	


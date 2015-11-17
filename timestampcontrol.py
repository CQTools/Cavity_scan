#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 12:59:51 2015

@author: Nick Lewty

Program to start and stop timestamp. It creates a filename based on the time the timestamp was started and
places in a directory structure depending on the year the year, the month and the day the data was taken. 
It can be called from the command line using positional arguments and extra flags
=================================================================================

usage: timestampcontrol.py [-h] [-of FILENAME] [-t SECONDS]
                           {fixedtime,start,stop}

Timestamp control generates new data file after each call with format
/home/qitlab/data/timestamp/year/month/day/starttime.timestamp

positional arguments:
  {fixedtime,start,stop}
                        Commands for running timestamp: Start runs
                        indefinatly, fixedtime runs for 1 hours unless -t flag
                        specified, Stop closes timestamp if running

optional arguments:
  -h, --help            show this help message and exit
  -of FILENAME          Appends optional text to filename
  -t SECONDS            Changes timestamp run length
		
=================================================================================

"""


import subprocess as sp
import time, os
import argparse
import datetime 

READPROG='/home/qitlab/programs/usbtimetagdriver/testapps/readevents3_withblanks'



#FUNCTION_MAP = {'start' : start(),'fixedtime' : fixedtime() }
                

def folder(base_folder='/home/qitlab/data/timestamp'):
	currentdate = str(datetime.date.today()).split('-')
	year = currentdate[0]
	month = currentdate[1]
	day =  currentdate[2]
	directory = base_folder + '/'+ year + '/'  + month + '/' + day  + '/'
	if not os.path.exists(directory):
		os.makedirs(directory)
	return directory
	

def filename(optional_name):
	currenttime = time.strftime( "%H:%M:%S")
	directory = folder()
	if optional_name == '':
		name = directory + optional_name  + currenttime + '.timestamp'
	else:
		name = directory + optional_name + '_'  + currenttime + '.timestamp'
	print 'Data file saved to \n' + name
	return name
	


def start():
	#outfile=filename(optional_name)
	outfile=filename('')
	sp.Popen([READPROG+' -e -a 1 > '+outfile],shell=True)
	print 'Timestamp started at ' + time.strftime( "%H:%M:%S")
	return outfile

def fixedtime():
	outfile=filename(optional_name)
	try:
		sp.Popen([READPROG+' -p 2 -e -a 1 -u -F > '+outfile],shell=True)
		print 'Timestamp running for ' + str(duration) +' seconds'
		print 'Use ctrl + C to terminate early'
		print 'Timestamp started at ' + time.strftime( "%H:%M:%S")
		time.sleep(duration) #s
		print 'Time elasped timestamp now stopped'
		stop()
	except KeyboardInterrupt:
		stop()


def stop():
	pid=sp.check_output(["pgrep -f readevents3"],shell=True).split()
	for i in range(len(pid)):
		sp.call(['kill '+str(pid[i])],shell=True)
	time.sleep(1)
	print 'Timestamp has been stopped by killing the process'
	print 'Timestamp terminated data stop recording at ' +  time.strftime( "%H:%M:%S")

"""Parser used for creating commandline options if it is called from the command line"""

parser = argparse.ArgumentParser(description='Timestamp control \n generates new data file after each call with format /home/qitlab/data/timestamp/year/month/day/starttime.timestamp')
parser.add_argument('-of',default='',help='Appends optional text to filename',dest='Filename')
parser.add_argument('-t',default=3600,help='Changes timestamp run length',type=int,dest='seconds')
FUNCTION_MAP = {'start' : start,'fixedtime':fixedtime,'stop' : stop }
parser.add_argument('command', choices=FUNCTION_MAP.keys(),help='Commands for running timestamp: Start runs indefinatly, fixedtime runs for 1 hours unless -t flag specified, Stop closes timestamp if running')
  
if __name__ == "__main__":                  
	args = parser.parse_args() 
	optional_name = args.Filename
	duration = args.seconds
	func = FUNCTION_MAP[args.command]
	func()                 



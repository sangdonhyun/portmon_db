import psycopg2 as pg2 
import datetime
import random
import time
import json
import ast
import ConfigParser
import os

# Testes on Python2.6


##Port Structure, Slot Number(0 if not exists), Port Number(Not 'Index'), CRC Error, Rx, Tx to Initialize
class Port:
	def __init__(self, index, slot, number, crc, rx, tx):
		self.index = index
		self.slot = slot
		self.number = number
		self.crc = crc
		self.rx = rx
		self.tx = tx

	def getData(self):
		return [self.index, self.slot, self.number, self.crc, self.rx, self.tx]

#Switch Structure, Serial and Total port count(Actual Data length to transfer)
class Switch:
	def __init__(self, serial, portCount):
		self.serial = serial
		self.portCount = portCount
		self.portItemCount = 6
		self.ports = []

	def addPort(self, port):
		self.ports.append(port)
	
	def getPortDataAsArray(self):
		result = []
		result.append(self.portCount)
		for port in self.ports:
			for p in port.getData():
				result.append(p)
		return result

	def getPortDataAsInsertFormatString(self):
		result = "{"
		result += str(self.portCount) + ","
		for port in self.ports:
			for p in port.getData():
				result += str(p) + ","

		if result.endswith(","):
			result = result[:-1]
		result += "}"
		return result

def generateDummyPortInfoAtTheMoment(cursor, pmap,store_time,event_time):
	checkTheMomentContainerTable(cursor)
	for switch in pmap.keys():
	
		indexmap = pmap[switch]
		#check switch data integrity
		swiCon = Switch(switch, len(indexmap))

		for index in indexmap.keys():
			portinfo = indexmap[index]
			if "tx" in portinfo.keys():
				port = Port(index, portinfo["slot"], portinfo["portnum"], portinfo["crcerr"], int(round(float(portinfo["rx"]))), int(round(float(portinfo["tx"]))))
			else:
				port = Port(index, portinfo["slot"], portinfo["portnum"], portinfo["crcerr"], -1, -1)
			swiCon.addPort(port)

		swiDataString = swiCon.getPortDataAsInsertFormatString()
		today = str(datetime.datetime.now())
		today = today[:today.find(" ")]
		today = today.replace("-", "_")

		#Query prepare
		query = """insert into perfom_swi.perform_swi_brocade_port_status_""" + today + """(store_time, event_time, swi_serial, data) values(%s, %s, %s, %s) returning swi_serial"""

		#Set Date format
		now = str(datetime.datetime.now())
		now = now[:now.find(".")]

		#print query % (now, swiCon.serial, swiDataString)
		try :
			cursor.execute(query, (store_time,event_time, swiCon.serial, swiDataString));
			result = cursor.fetchone();
			print "Query complete : ", result[:100]
			#print "query : ", query % (now, swiCon.serial, swiDataString)

		except pg2.DatabaseError, e:
			print "error creating database: %s", e

def checkTheMomentContainerTable(cursor):
	today = str(datetime.datetime.now())
	today = today[:today.find(" ")]
	today = today.replace("-", "_")
	createTableQuery = """CREATE TABLE IF NOT EXISTS perfom_swi.perform_swi_brocade_port_status_""" + today + """ (store_time text, event_time text, swi_serial character varying(50), data integer[])"""
	cursor.execute(createTableQuery)

#Connect to DB
def connectToQWEB(hostip):
	conn=pg2.connect(database="qweb",user="webuser",password="qw19850802@",host=hostip, port="5432")
	print "Connect to ", hostip
	return conn

	
	


def inst(lineset,store_time,event_time):
	
	cfg = ConfigParser.RawConfigParser()
	cfgfile= os.path.join('config','config.cfg')
	cfg.read(cfgfile)
	hostip=cfg.get('server','ip')

########################################
###			Start Sample
########################################
	conn = connectToQWEB(hostip)
	cursor = conn.cursor()
	
# 	with open('result.txt') as f:
# 	    lineset = f.readlines()
	
	hashmap = dict()
	for portinfo in lineset:
		
# 		print portinfo
# 		portinfo = ast.literal_eval(line)
# 		del portinfo["datetime"]
	
		if portinfo["serial"] in hashmap.keys():
			#print "portinfo : ", portinfo["serial"]
			map = hashmap[portinfo["serial"]]
			map.update({portinfo["portindex"] : portinfo})
		else:
			map = dict();
			map.update({portinfo["portindex"] : portinfo})
			hashmap.update({portinfo["serial"]: map})
	
	
	generateDummyPortInfoAtTheMoment(cursor, hashmap,store_time,event_time)
	conn.commit()		
	#print "MAP : ", hashmap
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
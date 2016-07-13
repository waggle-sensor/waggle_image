#!/usr/bin/env python3

import os, os.path, sys, zmq, time, subprocess, datetime, argparse, json
import urllib.request, urllib.error, urllib.parse
sys.path.append('../')
from waggle_protocol.protocol.PacketHandler import *
from waggle_protocol.utilities.pidfile import PidFile, AlreadyRunning

"""
    This module keeps the current time using outer sources such as beehive server or nodecontroller. To get time from beehive server this uses html request. If it does not work (e.g., no internet) the module tries to send a ti$
    The update happens periodically (e.g., everyday).
"""

BEEHIVE_IP="beehive1.mcs.anl.gov"
NODE_CONTROLLER_IP="10.31.81.10"
pid_file = "/var/run/waggle/epoch.pid"


def get_time_from_beehive():
	"""
		Tries to get data from beehive server. It retries NUM_OF_RETRY with a delay of 10 sec.
	"""
	URL = "http://%s/api/1/epoch" % (BEEHIVE_IP)
	NUM_OF_RETRY=5
	t = None
	while True:
		t = None
		try:
			response = urllib.request.urlopen(URL, timeout=10)
			msg = json.loads(response.read().decode('iso-8859-15'))
			t = msg['epoch']
			break
		except Exception as e:
			t = None
			NUM_OF_RETRY -= 1
			if NUM_OF_RETRY <= 0:
				break
			else:
				time.sleep(10)
	return t

def get_time_from_nc():
	HOST = NODE_CONTROLLER_IP
	PORT = 9090
	msg = None
	socket = None
	NUM_OF_RETRY=3
	t = None
	while True:
		try:
			context = zmq.Context()
			socket = context.socket(zmq.REQ)
			socket.connect ("tcp://%s:%s" % (HOST, PORT))
			socket.send("time".encode('iso-8859-15'))
			response = socket.recv().decode('iso-8859-15')
			socket.close()
			msg = json.loads(response)
			t = msg['epoch']
			break
		except zmq.error.ZMQError as e:
			t = None
			NUM_OF_RETRY -= 1
		except Exception as e:
			t = None
			NUM_OF_RETRY -= 1
			if NUM_OF_RETRY <= 0:
				break
	return t

        

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--force', dest='force', help='kill other processes and start', action='store_true')
	args = parser.parse_args()

	try:
		with PidFile(pid_file, force=args.force, name=os.path.basename(__file__)):
			current_time = datetime.datetime.now()
			next_period = current_time + datetime.timedelta(days=1)

			while True:
				current_time = datetime.datetime.now()
				if datetime.datetime.now().year < 2016 or next_period < current_time:
					# Try to get time from NC
					d = get_time_from_beehive()
					if not d:
						d = get_time_from_nc()

					if not d:
						time.sleep(10)
						continue
					else:
						try:
							subprocess.call(["date", "-s@%s" % (d)])
						except Exception as e:
							time.sleep(10)
							continue

					# Set next update
					current_time = datetime.datetime.now()
					next_period = current_time + datetime.timedelta(days=1)
				else:
					time.sleep(60)
	except AlreadyRunning as e:
		print("Please use supervisorctl to start and stop the Waggle Plugin Manager.")
	except KeyboardInterrupt:
		print("exiting...")
	except Exception as e:
		print("Error (%s): %s" % ( str(type(e)), str(e)))

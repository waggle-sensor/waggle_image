#!/usr/bin/env python3

import os, os.path, sys, zmq, time, subprocess, datetime, argparse, json
import logging
import urllib.request, urllib.error, urllib.parse
sys.path.append('../')
from waggle_protocol.protocol.PacketHandler import *
from waggle_protocol.utilities.pidfile import PidFile, AlreadyRunning

"""
    This module keeps the current time using outer sources such as beehive server or nodecontroller. To get time from beehive server this uses html request. If it does not work (e.g., no internet) the module tries to send a ti$
    The update happens periodically (e.g., everyday).
"""

#TODO: 

loglevel=logging.DEBUG
LOG_FORMAT='%(asctime)s - %(name)s - %(levelname)s - line=%(lineno)d - %(message)s'

root_logger = logging.getLogger()
root_logger.setLevel(loglevel)
formatter = logging.Formatter(LOG_FORMAT)

handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)

root_logger.handlers = []
root_logger.addHandler(handler)

logger = logging.getLogger(__name__)
logger.setLevel(loglevel)

BEEHIVE_HOST="beehive1.mcs.anl.gov"
NODE_CONTROLLER_IP="10.31.81.10"
pid_file = "/var/run/waggle/epoch.pid"


def get_time_from_beehive():
	"""
		Tries to get data from beehive server. It retries NUM_OF_RETRY with a delay of 10 sec.
	"""
	URL = "http://%s/api/1/epoch" % (BEEHIVE_HOST)
	NUM_OF_RETRY=5
	t = None
	while True:
		t = None
		try:
			response = urllib.request.urlopen(URL, timeout=10)
			msg = json.loads(response.read().decode('iso-8859-15'))
			t = msg['epoch']
			logger.debug("Got time from %s: %s" % (URL, msg))
			break
		except Exception as e:
			t = None
			logger.debug("Failed to get time from the server")
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
			socket.set(zmq.ZMQ_RCVTIMEO, 3000)
			socket.set(zmq.ZMQ_SNDTIMEO, 3000)
			socket.connect ("tcp://%s:%s" % (HOST, PORT))
			socket.send("time".encode('iso-8859-15'))
			response = socket.recv().decode('iso-8859-15')
			socket.close()
			msg = json.loads(response)
			t = msg['epoch']
			logger.debug("Got time from %s:%d: %s" % (HOST, PORT, msg))
			break
		except zmq.error.ZMQError as e:
			t = None
			logger.debug("ZMQ Failed to get time from NC:%s", (str(e)))
			NUM_OF_RETRY -= 1
		except Exception as e:
			t = None
			logger.debug("Failed to get time from NC:%s", (str(e)))
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
			logger.info("epoch service started")
			current_time = datetime.datetime.now()
			next_period = current_time + datetime.timedelta(days=1)

			while True:
				current_time = datetime.datetime.now()
				if datetime.datetime.now().year < 2016 or next_period < current_time:
					logger.info("current time: %s, update needed" % (current_time))
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
							logger.debug("Failed to set time:%s", (str(e)))
							continue

					# Set next update
					current_time = datetime.datetime.now()
					next_period = current_time + datetime.timedelta(days=1)
				else:
					time.sleep(60)
	except AlreadyRunning as e:
		logger.debug("Please use waggle-service to start and stop this service.")
	except KeyboardInterrupt:
		logger.debug("exiting...")
	except Exception as e:
		logger.debug("Error (%s): %s" % ( str(type(e)), str(e)))

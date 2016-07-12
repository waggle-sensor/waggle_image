#!/usr/bin/env python3

import zmq, time, subprocess, datetime, argparse, json
import urllib.request, urllib.error, urllib.parse
sys.path.append('../')
from waggle_protocol.protocol.PacketHandler import *
from waggle_protocol.utilities.pidfile import PidFile, AlreadyRunning

"""
	This module keeps the current time using outer sources such as beehive server or nodecontroller. To get time from beehive server this uses html request. If it does not work (e.g., no internet) the module tries to send a time request to any attached nodecontroller (even itself) according to waggle protocol.
	The update happens periodically (e.g., everyday).
"""

BEEHIVE_IP="beehive1.acs.anl.gov"
NODE_CONTROLLER_IP="10.31.81.10"

def get_time_from_beehive():
	"""
		Tries to get data from beehive server. It retries NUM_OF_RETRY with a delay of 10 sec.
	"""
    URL = "http://%s/api/1/epoch" % (BEEHIVE_IP)
    NUM_OF_RETRY=5
    while True:
	    try:
	    	response = urllib.request.urlopen(HOST, timeout=10)
	    	time = json.loads(response.read().decode('utf-8'))
	    	return time['epoch']
	    except Exception as e:
	    	NUM_OF_RETRY -= 1
	    	if NUM_OF_RETRY <= 0:
	    		break
	    	else
	    		time.sleep(10)
	return None

def get_time_from_nc():
    HOST = NODE_CONTROLLER_IP
    PORT = 9090
    msg = None
    socket = None
    NUM_OF_RETRY=3
    while True:
	    try:
	        context = zmq.Context()
	        socket = context.socket(zmq.REQ)
	        socket.connect ("tcp://%s:%s" % (HOST, PORT))
	        socket.send("time")
	        msg = socket.recv()
	        socket.close()
	        time = json.loads(msg)
	    	return time['epoch']
	    except zmq.error.ZMQError as e:
	        msg = None
	        NUM_OF_RETRY -= 1
	    except Exception as e:
	    	msg = None
	    	NUM_OF_RETRY -= 1
	    if NUM_OF_RETRY <= 0:
	    	break
    	
    return None

        

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
    parser.add_argument('--logging', dest='enable_logging', help='write to log files instead of stdout', action='store_true')
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
				            subprocess.call(["date", "-s@%s" % (msg)])
				        except Exception as e:
				        	continue

				    # Set next update
				    current_time = datetime.datetime.now()
            		next_period = current_time + datetime.timedelta(days=1)
                else:
                	time.sleep(60)
    
    except AlreadyRunning as e:
        logger.error(str(e))
        logger.error("Please use supervisorctl to start and stop the Waggle Plugin Manager.")
    except KeyboardInterrupt:
        logger.error("exiting...")
    except Exception as e:
        logger.error("Error (%s): %s" % ( str(type(e)), str(e)))

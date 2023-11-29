#!/usr/bin/python
import logging
import signal
import sys

import cherrypy

from . motionsensor import MotionSensor
from . configuration import PyMotionConfig
from . webapp import PyMotionWeb

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

config = PyMotionConfig.load_config()
ms = MotionSensor(config)

def do_exit(*args):
    logging.getLogger().info("Terminate signal recieved - waiting for cycle to finish")
    ms.should_terminate = True
    cherrypy.engine.exit()

signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGTERM, do_exit)

ms.start()
cherrypy.quickstart(PyMotionWeb(ms), "/", 'cherrypy.conf')

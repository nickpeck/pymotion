#!/usr/bin/python
import logging
import signal
import sys

import cherrypy
from cherrypy.lib import auth_digest

from . motionsensor import MotionSensor
from . configuration import PyMotionConfig
from . webapp import PyMotionWeb

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

config = PyMotionConfig.load_config()
ms = MotionSensor(config)

def do_exit(*args):
    logging.getLogger().info(
        "Terminate signal recieved - waiting for cycle to finish")
    ms.should_terminate = True
    cherrypy.engine.exit()

signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGTERM, do_exit)

ms.start()
cherrypy.server.socket_host = config.serverHost
cherrypy.server.socket_port = config.serverPort
cp_users = {config.username: config.password}
cp_conf = {
   '/': {
        'tools.auth_digest.on': True,
        'tools.auth_digest.realm': 'localhost',
        'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(cp_users),
        'tools.auth_digest.key': 'a565c27146791cfb',
        'tools.auth_digest.accept_charset': 'UTF-8',
   }
}
cherrypy.quickstart(PyMotionWeb(ms), "/", cp_conf)

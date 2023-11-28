#!/usr/bin/python
import signal
from . motionsensor import MotionSensor
from . configuration import PyMotionConfig

config = PyMotionConfig.load_config()
ms = MotionSensor(config)

def do_exit():
    ms.isRunning = False

signal.signal(signal.SIGINT, do_exit)
signal.signal(signal.SIGTERM, do_exit)

ms.start()

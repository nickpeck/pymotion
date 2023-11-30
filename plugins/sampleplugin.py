"""
illustrates a plugin
"""

import logging
from PIL.BmpImagePlugin import BmpImageFile

def on_motion_detected(
            threatRating,
            image1: BmpImageFile,
            image2: BmpImageFile,
            diff: BmpImageFile,
            config: dict):
    logging.getLogger().info(config['greeting'])

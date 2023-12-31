import os
import datetime
import importlib
import math
import logging
import stat
import glob
from threading import Thread
import traceback
from time import sleep
from shutil import copy, rmtree

import pygame
import pygame.camera
from pygame.locals import *
from PIL import Image, ImageChops
from PIL.BmpImagePlugin import BmpImageFile
import numpy as np

from . configuration import PyMotionConfig

logger = logging.getLogger()

ARCHIVE_DIR = "archive"
PLUGINS_DIR = "plugins"

class MotionSensor(Thread):

    def __init__(self, config: PyMotionConfig):
        super(MotionSensor, self).__init__()
        self.config = config
        self.should_terminate = False
        self.is_running = True
        pygame.init()
        pygame.camera.init()
        self.plugins = self._load_plugins()
        logger.info("Loaded plugins: {}".format(list(self.plugins.keys())))
        cameraList = pygame.camera.list_cameras()
        if not cameraList:
            logger.error("No cameras. Exiting.")
            exit(1)
        logger.info("Discovered cameras: {}".format(cameraList))
        try:
            self.camera = pygame.camera.Camera(self.config.cameraName, (800, 800))
            logger.info("Initialized using specified camera '{}'".format(self.config.cameraName))
        except ValueError:
            logger.warn("Camera '{}' not found. Using camera '{}'".format(self.config.cameraName, cameraList[0]))
            self.camera = pygame.camera.Camera(cameraList[0], (800, 800))
        self.camera.start()

    def run(self):
        logger.info("Initialising camera")
        # give camera time to adjust to light levels or you will get an alert on first run
        sleep(self.config.initialWaitPeriodSeconds)
        while True:
            if self.should_terminate:
                break
            if os.path.getsize(ARCHIVE_DIR) / 1000000 > self.config.maxArchiveSizeMB:
                self._purge_archive_dir()
            self._rotate_archive_contents()
            if self.is_running:
                self._capture_and_compare()
            else:
                try:
                    self.camera.stop()
                except SystemError:
                    pass
            sleep(self.config.pollingIntervalSeconds)
        logger.info("Terminated")
        self.camera.stop()
		
    def suspend(self):
        self.is_running = False

    def resume(self):
        if self.is_running:
            return
        self.camera.start()
        self.is_running = True

    def _load_plugins(self):
        plugins = {}
        plugin_modules = glob.glob(os.path.join(PLUGINS_DIR, "*.py"))
        mod_names = [ os.path.basename(f)[:-3] for f in plugin_modules if os.path.isfile(f) and not f.endswith('__init__.py')]
        for mod_name in mod_names:
            conf = self.config.plugins.get(mod_name, None)
            if conf is None:
                continue
            try:
                plugins[mod_name] = {
                    "module": importlib.import_module("plugins." + mod_name),
                    "config": conf
                }
            except ModuleNotFoundError as mnfe:
                logger.warn("Could not load plugin {}: {}".format(mod_name, mnfe.msg))
        return plugins
		
    def _capture_and_compare(self):
        file1 = os.path.join(ARCHIVE_DIR, "ImageA.bmp")
        file2 = os.path.join(ARCHIVE_DIR, "ImageB.bmp")
        key_image = os.path.join(ARCHIVE_DIR, "key_image.bmp")
        logger.info("taking photo1")
        self._capture_image(file1)
        logger.info("...ok. pausing...")
        sleep(self.config.photoIntervalSeconds)
        logger.info("taking photo2")
        self._capture_image(file2)
        logger.info("making histogram:")
        self._save_histogram(file1, file2, key_image)
        key_image_data = Image.open(key_image)
        entropy = self._image_entropy(key_image_data)
        logger.info("entropy is {}".format(entropy))
        if entropy > self.config.threshold:
            self.on_motion_detected(entropy, Image.open(file1), Image.open(file2), key_image_data)

    def _capture_image(self, save_as_name: str):
        surface = self.camera.get_image()
        pygame.image.save(surface, save_as_name)

    def _save_histogram(self, file1: str, file2: str, save_as_name: str):
        f1 = Image.open(file1)
        f2 = Image.open(file2)
        img = ImageChops.difference(f1, f2)
        img.save(save_as_name)

    def _image_entropy(self, img: BmpImageFile):
        w,h = img.size
        a = np.array(img.convert('RGB')).reshape((w*h,3))
        h,e = np.histogramdd(a, bins=(16,)*3, range=((0,256),)*3)
        prob = h/np.sum(h) # normalize
        prob = prob[prob>0] # remove zeros
        return -np.sum(prob*np.log2(prob))

    def _rotate_archive_contents(self):
        delta = datetime.timedelta(days=self.config.archiveRetentionDays)
        for obj in os.listdir(ARCHIVE_DIR):
            stats = os.stat(os.path.join(ARCHIVE_DIR, obj))
            if not stat.S_IFDIR:
                continue
            if datetime.datetime.fromtimestamp(stat.ST_CTIME) > datetime.datetime.now() - delta:
                log.warn("Archive directory '{}' is older than retention period and will be removed")
                rmtree(os.path.join(ARCHIVE_DIR, obj))

    def _purge_archive_dir(self):
        log.warn("Archive directory is larger than {}MB and will be purged.".format(self.config.maxArchiveSizeMB))
        for obj in os.listdir(ARCHIVE_DIR):
            if not stat.S_IFDIR:
                continue
            rmtree(obj)

    def on_motion_detected(
            self,
            threatRating,
            image1: BmpImageFile,
            image2: BmpImageFile,
            diff: BmpImageFile):
        logger.info("Motion alert! Archiving images.")
        data_prefix = datetime.datetime.now().isoformat().replace(":", "-")
        os.mkdir(os.path.join(ARCHIVE_DIR, data_prefix))
        copy(
            os.path.join(ARCHIVE_DIR, "ImageA.bmp"),
            os.path.join(ARCHIVE_DIR, data_prefix, "ImageA.bmp"))
        copy(
            os.path.join(ARCHIVE_DIR, "ImageB.bmp"),
            os.path.join(ARCHIVE_DIR, data_prefix, "ImageB.bmp"))
        copy(
            os.path.join(ARCHIVE_DIR, "key_image.bmp"),
            os.path.join(ARCHIVE_DIR, data_prefix, "key_image.bmp"))
        for name, plugin in self.plugins.items():
            try:
                plugin['module'].on_motion_detected(
                    threatRating,
                    image1,
                    image2,
                    diff,
                    plugin['config'])
            except Exception as e:
                logger.warn(traceback.format_exc())

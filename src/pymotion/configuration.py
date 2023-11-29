import os
from dataclasses import dataclass, field
import logging
from typing import Dict, Any

import yaml

logger = logging.getLogger()

@dataclass
class PyMotionConfig:
    initialWaitPeriodSeconds: int = 5
    pollingIntervalSeconds: int = 10
    photoIntervalSeconds: int =1
    threshold: float = 0.5
    cameraName: str = "Integrated Webcam"
    archiveDirectory: str = "archive"
    modulesDirectory: str = "./src/modules"
    archiveRetentionDays: int = 10
    maxArchiveSizeMB: int = 500
    serverPort:int = 8080
    modules: Dict[str, Any] = field(default_factory = lambda: {})

    @staticmethod
    def load_config():
        opts = {}
        try:
            with open('pymotion.yaml', 'r') as file:
                opts.update(yaml.safe_load(file)['pymotion'])
        except FileNotFoundError:
            logger.warn("No pymotion.yaml found, initializing using defaults")
        return PyMotionConfig(**opts)

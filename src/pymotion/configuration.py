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
    archiveRetentionDays: int = 10
    maxArchiveSizeMB: int = 500
    serverPort: int = 8080
    serverHost: str = "0.0.0.0"
    username: str = "admin"
    password: str = "secret"
    plugins: Dict[str, Any] = field(default_factory = lambda: {})

    @staticmethod
    def load_config():
        opts = {}
        try:
            with open('pymotion.yaml', 'r') as file:
                yaml_opts = yaml.safe_load(file)
                opts.update(yaml_opts['pymotion'])
                opts.update(yaml_opts['server'])
                try:
                    opts.update({"plugins": yaml_opts["plugins"]})
                except KeyError:
                    pass
        except FileNotFoundError:
            logger.warn("No pymotion.yaml found, initializing using defaults")
        return PyMotionConfig(**opts)


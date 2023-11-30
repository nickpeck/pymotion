"""
Send an alert via AWS SNS. Customize to your needs...
"""

import logging

import boto3
from PIL.BmpImagePlugin import BmpImageFile

sns = boto3.client('sns')

def on_motion_detected(
            threatRating,
            image1: BmpImageFile,
            image2: BmpImageFile,
            diff: BmpImageFile,
            config: dict):
    logging.getLogger().info("Sending SNS Message")
    sns.publish(
        TopicArn=config["topicARN"],
        Message="Motion Sensor Alert at rating {}".format(threatRating),
        Subject="Motion Sensor Alert"
    )

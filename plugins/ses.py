"""
Send an alert via AWS SES. Customize to your needs...
"""

import datetime
import logging

import boto3
from PIL.BmpImagePlugin import BmpImageFile

ses = boto3.client('ses')

def on_motion_detected(
            threatRating,
            image1: BmpImageFile,
            image2: BmpImageFile,
            diff: BmpImageFile,
            config: dict):
    date = datetime.datetime.now().isoformat()
    logging.getLogger().info("Sending SES Email")
    ses.send_email(
        Source=config["source"],
        Destination={
            "ToAddresses": config["toAddresses"]
        },
        Message={
            "Subject": {
                "Data": "Motion Sensor Alert at {}".format(date),
                "Charset": "utf-8"
            },
            "Body": {
                "Text": {
                    "Data": "Motion Sensor Alert at {}. Please log into your device for more details {}.".format(date, config['deviceUrl']),
                    "Charset": "utf-8"
                }
            }
        }
    )


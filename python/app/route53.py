import os
import sys
import boto3
import logging

# Setup logger
LOG_FORMAT = '%(asctime)s %(levelname)s %(module)s : %(message)s'
stdout_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("../log/application.log")
handlers = [stdout_handler, file_handler]

logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=handlers)
logger = logging.getLogger(__name__)

class Route53:
    """
    A Class to interact with AWS Route53
    """
    def __init__(self):
        logger.info(f"Inside __init__ of Route53 class")
        self.aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self.hosted_zone_id = "/hostedzone/Z31X3CKBZG9JSR"

    def add_cname(self, name, value):
        """
        Adds CNAME record
        """
        logger.info("Adding CNAME record on AWS Route53")
        logger.info(f"CNAME record mapping: {name} --> {value}")
        client = boto3.client('route53',
                aws_access_key_id = self.aws_access_key_id,
                aws_secret_access_key = self.aws_secret_access_key
                )
        client.change_resource_record_sets(
            HostedZoneId = self.hosted_zone_id,
            ChangeBatch = {
                            'Comment': f'add {name} -> {value}',
                            'Changes': [{
                                'Action': 'UPSERT',
                                'ResourceRecordSet': {
                                    'Name': name,
                                    'Type': 'CNAME',
                                    'TTL': 300,
                                    'ResourceRecords': [{'Value': value}]
                                }
                            }]
                          }
            )
        logger.info("Successfully added CNAME record on AWS Route53")

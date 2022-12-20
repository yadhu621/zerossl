from ast import parse
import os
import sys
import logging
import pathlib
import argparse
from zerossl import ZeroSSL


def main():
    """
    main() function
    """
    # Create log directory if not present
    pathlib.Path('../log/').mkdir(parents=True, exist_ok=True)
    
    # Setup logger
    log_format = '%(asctime)s %(levelname)s %(module)s : %(message)s'
    stdout_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler("../log/application.log")
    handlers = [stdout_handler, file_handler]

    logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)
    logger = logging.getLogger(__name__)

    api_key = os.environ.get("ZEROSSL_API_KEY")
    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")


    if api_key is None:
        logger.info("ZEROSSL_API_KEY environment variable is not set. Exiting...")
        exit()
        
    if aws_access_key_id is None:
        logger.info("AWS_ACCESS_KEY_ID environment variable is not set. Exiting...")
        exit()
        
    if aws_secret_access_key is None:
        logger.info("AWS_SECRET_ACCESS_KEY environment variable is not set. Exiting...")
        exit()

    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--domain-name',required=True)
    args = parser.parse_args()

    subdomain = args.domain_name
 

    # create cert directory if not present
    pathlib.Path('../cert/'+ subdomain).mkdir(parents=True, exist_ok=True)
    logger.info(f"Creating cert/ and cert/{subdomain} directories to store certificates")


    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--domain-name',required=True)
    args = parser.parse_args()

    subdomain = args.domain_name
    zerossl = ZeroSSL(api_key, subdomain)
    zerossl.generate_csr().request_certificate().request_validation().download()

if __name__ == "__main__":
    main()

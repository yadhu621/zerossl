import sys
import json
import time
import logging
import requests
import pathlib
from openssl import SSL
from route53 import Route53

# Create log directory if not present
pathlib.Path('../log/').mkdir(parents=True, exist_ok=True)

# Setup logger
log_format = '%(asctime)s %(levelname)s %(module)s : %(message)s'
stdout_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("../log/application.log")
handlers = [stdout_handler, file_handler]

logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)
logger = logging.getLogger(__name__)

class ZeroSSL:
    """
    A class to interact with ZeroSSL over REST API
    """
    def __init__(self, api_key, subdomain) -> None:

        self.base_url = "https://api.zerossl.com"
        self.api_key = api_key
        self.url = self.base_url + '/certificates?access_key=' + self.api_key
        self.subdomain = subdomain

        self.csr = ""
        self.cname_record_name = ""
        self.cname_record_value = ""
        self.certificate_id = ""

    def certificates(self):
        """
        Return all certficates with expiry and status, as a list of dicts

        :return:
        [
            {
                "name": "stackstorm.amyra.co.uk",
                "expires" : "2022-08-14",
                "status" : "draft"
            },
            {
                "name": "argocd.amyra.co.uk",
                "expires" : "2022-08-10",
                "status" : "issued"
            }
        ]
        :rtype: list
        """
        response = requests.get(self.url)
        response = response.json()
        results = response["results"]

        logger.info(json.dumps(results, indent=4, sort_keys=True))

        certificates = []
        for result in results:
            common_name = result["common_name"]
            expires = result["expires"]
            status = result["status"]
            certificate = {'name' : common_name, 'expires': expires, 'status': status}

            certificates.append(certificate)

        return certificates

    def generate_csr(self):
        """
        Invokes generate_key_csr method of SSL Class.
        Saves returned CSR in a variable within the object

        :return: object
        :rtype: Object of Type ZeroSSL
        """
        logger.info(f"Inside generate_csr() method of ZeroSSL class")
        logger.info(f"Initiating CSR creation steps for subdomain : {self.subdomain}")
        logger.info(f"Invoking SSL() class")
        ssl = SSL(self.subdomain)
        self.csr = ssl.generate_key_csr()

        return self

    def request_certificate(self):
        """
        Submit CSR to ZeroSSL to request a certificate

        :return: object
        :rtype: Object of Type ZeroSSL
        """
        logger.info(f"Inside request_certificate() method of ZeroSSL class")
        payload = {'certificate_domains': self.subdomain,
                   'certificate_validity_days': 90,
                   'certificate_csr': self.csr}

        logger.info(f"Requesting certificate from zerossl api")
        # logger.info("Payload:")
        # logger.info("=================")
        # logger.info(f"{payload}")
        # logger.info("=================")
        response = requests.post(self.url, data=payload)
        result = json.loads(response.text)

        logger.info("Received response from zerossl api")
        # logger.info("Response:")
        # logger.info("=================")
        # logger.info(json.dumps(result, indent=4))
        # logger.info("=================")

        self.certificate_id = result['id']

        result_cname = result['validation']['other_methods'][self.subdomain]
        self.cname_record_name = result_cname['cname_validation_p1']
        self.cname_record_value = result_cname['cname_validation_p2']

        logger.info("Certificate request with zerossl api completed.")
        logger.info("Logon to https://app.zerossl.com/certificates/draft to confirm")
        logger.info("Will trigger verify request after 15 seconds")
        time.sleep(15)
        return self

    def request_validation(self):
        """
        Verifies certificate with ZeroSSL using DNS (CNAME) validation

        :return: object
        :rtype: Object of Type ZeroSSL
        """
        logger.info(f"Inside request_validation() method of ZeroSSL class")

        request_validation_url = self.base_url + '/certificates/' + self.certificate_id + '/challenges?access_key=' + self.api_key
        
        logger.info(f"Invoking Route53() class to set CNAME record")
        Route53().add_cname(self.cname_record_name, self.cname_record_value)

        # Submission of request_validation succeeds only on a positive CNAME Lookup, so retry until CNAME record propagates
        # Submission of request_validation is successful when 'status' moves to 'pending_validation'

        logger.info(f"Submitting a request_validation with zerossl api...")
        logger.info(f"NOTE: Submission of request_validation succeeds only on successful CNAME Lookup")
        logger.info(f"NOTE: Retry submitting request_validation until we successfully can")
        logger.info(f"NOTE: When submit succeeds, status moves to 'pending_validation'")
        retry = 0
        max_retries = 5
        while retry < max_retries:
            logger.info(f"Submit Retry attempt : {retry}")
            logger.info("Invoking request_validation_url... (validation_method: CNAME_CSR_HASH)")
            response = requests.post(request_validation_url, data={'validation_method': 'CNAME_CSR_HASH'})
            result = json.loads(response.text)

            logger.info("Received response from zerossl api")
            # logger.info("Response:")
            # logger.info("=================")
            # logger.info(json.dumps(result, indent=4))
            # logger.info("=================")

            if 'error' in result:
                logger.info("Inside continue loop...")
                retry += 1
                time.sleep(2**retry)
                # logger.info("Response with 'error'':")
                # logger.info("=================")
                # logger.info(json.dumps(result, indent=4))
                # logger.info("=================")
                continue

            if 'status' in result and result['status'] == 'pending_validation':
                logger.info("Inside break loop")
                logger.info(f"Certificate status : {result['status']}")
                # logger.info("Response with no 'error':")
                # logger.info("=================")
                # logger.info(json.dumps(result, indent=4))
                # logger.info("=================")
                break

        logger.info("Submission of request_validation successful. Proceeding to download certificate.")
        return self

    def download(self):
        """

        """
        logger.info(f"Inside download() method of ZeroSSL class")

        validation_status_url = self.base_url + '/certificates/' + self.certificate_id + '/status?access_key=' + self.api_key
        download_url = self.base_url + '/certificates/' + self.certificate_id + '/download?access_key=' + self.api_key

        # Certificate download is possible only when status moves to "pending_validation" to "Issued" (i.e. validation_status = 1)
        # Status move from "pending_validation" to "Issued" takes approx. 8-10 minutes
        # Retry certificate download until validation_status changes to 1, then download
        logger.info(f"NOTE: Certificate download is possible only when certificate_status is 'Issued' (i.e. validation_status = 1)")
        logger.info(f"Retry checking validation_status until it changes to 1, then download")

        retry = 0
        max_retries = 20
        while retry < max_retries:
            logger.info("Calling validation_status_url")
            response = requests.get(validation_status_url)
            result = json.loads(response.text)
            validation_status = result['validation_completed']
            logger.info(f"Validation status : {validation_status}")

            if validation_status == 1:
                logger.info("Certificate status : 'Issued'. Downloading certificate...")
                response = requests.get(download_url)

                download_dir = "../cert/" + self.subdomain + '/'
                download_path = download_dir  + self.subdomain
                open(f"{download_path}.zip", "wb").write(response.content)
                break

            if validation_status == 0:
                retry += 1
                time.sleep(2**retry) # time.sleep(32)
                logger.info(f"Retry attempt : {retry}")
                continue

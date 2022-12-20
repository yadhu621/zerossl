from re import sub
import sys
import logging
import pathlib
from OpenSSL import crypto

# Create log directory if not present
pathlib.Path('../log/').mkdir(parents=True, exist_ok=True)

# Setup logger
log_format = '%(asctime)s %(levelname)s %(module)s : %(message)s'
stdout_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler("../log/application.log")
handlers = [stdout_handler, file_handler]

logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers)
logger = logging.getLogger(__name__)

class SSL:
    """
    A class to generate keys and certs
    """
    def __init__(self, subdomain) -> None:

        logger.info(f"Inside __init__ of SSL class")
        self.type_rsa = crypto.TYPE_RSA

        self.cn = subdomain
        self.keypath = '../cert/' + subdomain + '/' + self.cn + '.key'
        self.csrpath = '../cert/' + subdomain + '/' + self.cn + '.csr'
        self.crtpath = '../cert/' + subdomain + '/' + self.cn + '.crt'

        # create log directory if not present
        pathlib.Path('../cert/'+ subdomain).mkdir(parents=True, exist_ok=True)
        logger.info(f"Creating {subdomain}/ directory within log/ to store CSR, key")
        
    #Generate the key
    def generate_key_csr(self):
        """
        Generate a private key and CSR, and write to file
        Return the CSR

        :return: CSR
        :rtype: string
        """
        logger.info(f"Generating private key...")

        key = crypto.PKey()
        key.generate_key(self.type_rsa, 4096)
        with open(self.keypath, "w") as file:
            file.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode('utf-8'))

        logger.info(f"Saving private key for {self.cn} at {self.keypath}")

        country   = 'UK'
        state  = 'Berkshire'
        location   = 'Reading'
        organization   = 'Jubilee'
        organization_unit  = 'Homelab'

        req = crypto.X509Req()
        req.get_subject().CN = self.cn
        req.get_subject().C = country
        req.get_subject().ST = state
        req.get_subject().L = location
        req.get_subject().O = organization
        req.get_subject().OU = organization_unit
        req.set_pubkey(key)
        req.sign(key, "sha256")

        logger.info(f"Generating CSR for {self.cn}...")

        with open(self.csrpath, "w") as file:
            file.write(crypto.dump_certificate_request(crypto.FILETYPE_PEM, req).decode('utf-8'))

        logger.info(f"Saving CSR at {self.csrpath}")

        with open(self.csrpath, 'r') as file:
            csr = file.read().replace('\n', '')

        return csr

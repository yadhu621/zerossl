import os
from zerossl import ZeroSSL


def main():
    """
    main() function
    """

    api_key = os.environ.get("ZEROSSL_API_KEY")
    subdomain = os.environ.get("SUBDOMAIN")

    zerossl = ZeroSSL(api_key, subdomain)
    zerossl.generate_csr() \
            .request_certificate() \
            .request_validation() \
            .download()

if __name__ == "__main__":
    main()

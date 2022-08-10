# zerossl-app
Python script to automate certificate generation with ZeroSSL

## How to run
```
export ZEROSSL_API_KEY='96xxxf1cf7xxxxxxxcf56dxxxxc31'
export AWS_ACCESS_KEY_ID='AKIAxxxxxEWOFPxxxx5Axx'
export AWS_SECRET_ACCESS_KEY='LujmxxxxxxCpyAxxxxbkcLEvxxxxxJgu5'
export SUBDOMAIN='argocd.amyra.co.uk'

cd python/
virtualenv venv
./venv/Scripts/activate
pip install -r requirements.txt

cd app/
python main.py
```
Certificate will be downloaded to cert/ folder.
Logs will be written to application.log in log/ folder.


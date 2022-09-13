import requests
import json
import urllib3
import csv
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = "https://<IP>:<AdminPort>/api/v2/"
url_login= base_url + "authentication"

csv_header = ['port','untagged','tagged']
csv_path = os.path.dirname(__file__)
# Start Session to keep cookies
sess = requests.session()

#Login request
payload = {'username' : 'admin', 'secretkey' : 'changeit'}
res = sess.post(url_login, json=payload, verify=False )

# Read CSRFTOKEN and add it to the Header
for cookie in sess.cookies:
            if 'ccsrftoken' in cookie.name:
                csrftoken = cookie.value[1:-1]
                sess.headers.update({'X-CSRFTOKEN': csrftoken})

res = sess.get(base_url + "/wifi/managed_ap", verify=False)

resp_dict = res.json()
for ap in resp_dict['results']:
    ports = []

    print("Access-Point: %s / Local-IP: %s" % (ap['name'], ap['local_ipv4_addr']))

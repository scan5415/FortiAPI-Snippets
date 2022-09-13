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

res = sess.get(base_url + "/cmdb/switch-controller/managed-switch", verify=False)

resp_dict = res.json()
for switch in resp_dict['results']:
    ports = []

    print("Switch: %s" % (switch['name']))

    with open(csv_path + switch['name'] + ".csv", 'w',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

        for port in switch['ports']:
            vlans = port['allowed-vlans']
            if(port['allowed-vlans-all'] == 'enable'):
                vlans = "All"

            port = [port['port-name'], port['vlan'],vlans]
            writer.writerow(port)

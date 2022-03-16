import requests
import json
import urllib3
import csv
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
base_url = "https://fortiems.shl-group.com/api/v1/"
url_login= base_url + "auth/signin"

csv_header = ['Endpoint Name','Username','IP Address','Policy','FortiClient installed','Is registered on FortiEMS','Is excluded in FortiEMS']
csv_path = os.path.dirname(__file__)

endpoints_start = 4000
endpoints_count = 2000
endpoints_end = endpoints_start + endpoints_count

csv_filename = "\FortiEMS-EndpointsExport_%s-%s.csv"%(endpoints_start,endpoints_end)

# Start Session to keep cookies
sess = requests.session()

#Login request
payload = {'name' : 'admin', 'password' : '0ZBiRA9HsTamagxHKQif5RgBsK6CLnRlhmzFvZbZJ0G8fs2oGGp5TAK6Emu2DDoE'}
res = sess.post(url_login, json=payload, verify=False )

print(res.json()['result']['message'])

# Read CSRFTOKEN and add it to the Header
for cookie in sess.cookies:
            if 'ccsrftoken' in cookie.name:
                csrftoken = cookie.value[1:-1]
                sess.headers.update({'X-CSRFTOKEN': csrftoken})

param = {'offset':endpoints_start, 'count':endpoints_count, 'ems-call-type':'2'}
res = sess.get(base_url + "endpoints/index", params=param, verify=False)
print(res.json()['result']['message'])
resp_dict = res.json()
with open(csv_path + csv_filename, 'w',newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)

    for endpoint in resp_dict['data']['endpoints']:
        row = []

        print("Endpoint %s exported." % (endpoint['name']))

        row = [endpoint['name'], endpoint['username'], endpoint['ip_addr'], endpoint['endpoint_policy_name'], endpoint['is_installed'], endpoint['is_ems_registered'], endpoint['is_excluded']]

        writer.writerow(row)

print("File saved at %s%s" % (csv_path,csv_filename))

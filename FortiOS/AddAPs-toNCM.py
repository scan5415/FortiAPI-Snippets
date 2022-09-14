""" Generate FortiGate NAT Object based on a comma separated txt file list

This script generate FortiGate NAT CLI objects as output. Input is a comma
separated txt file. on each line is a new object.
The Input file need following format:
<externalIP> <internalIP> <comment>
(see description in the README file)

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Andy Scherer"
__contact__ = "ofee42@gmail.com"
__copyright__ = "Copyright 2022, Andy Scherer"
#__credits__ = ["None"]
__date__ = "2022/09/13"
__deprecated__ = False
__email__ =  "ofee42@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.0.1"


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

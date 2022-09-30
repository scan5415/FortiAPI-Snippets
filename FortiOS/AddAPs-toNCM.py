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
import re
from orionsdk import SwisClient

def FortiGateAPI_logon(base_url):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    url_login= base_url + "authentication"

    csv_header = ['port','untagged','tagged']
    csv_path = os.path.dirname(__file__)
    # Start Session to keep cookies
    sess = requests.session()

    #Login request
    payload = {'username' : 'fwadmin', 'secretkey' : '2UeJhxe5epfcf9Vqi3vS9bLnymKK3mde'}
    res = sess.post(url_login, json=payload, verify=False )

    # Read CSRFTOKEN and add it to the Header
    for cookie in sess.cookies:
                if 'ccsrftoken' in cookie.name:
                    csrftoken = cookie.value[1:-1]
                    sess.headers.update({'X-CSRFTOKEN': csrftoken})

    return sess

def FortiGateAPI_readAP(sess):
    res = sess.get(base_url + "/monitor/wifi/managed_ap", verify=False)

    resp_dict = res.json()
    for ap in resp_dict['results']:
        ports = []

        print("Access-Point: %s " % (ap))

def NCM_logon(server,username,password):
    swis = SwisClient(server, username, password)
    print("Login to NCM")
    return swis

def NCM_createNode(client,IPaddr,SNMPcommunity):
    # set up property bag for the new node
    props = {
        'Caption': 'Test-AP1',
        'IPAddress': IPaddr,
        'EngineID': 1,
        'ObjectSubType': 'SNMP',
        'SNMPVersion': 2,
        'Community': SNMPcommunity,

        'DNS': '',
        'SysName': ''
    }
    print("Adding node {}... ".format(props['IPAddress']), end="")
    results = client.create('Orion.Nodes', **props)
    print("DONE!")

    # extract the nodeID from the result
    nodeid = re.search(r'(\d+)$', results).group(0)

    pollers_enabled = {
        'N.Status.ICMP.Native': True,
        'N.Status.SNMP.Native': False,
        'N.ResponseTime.ICMP.Native': True,
        'N.ResponseTime.SNMP.Native': False,
        'N.Details.SNMP.Generic': True,
        'N.Uptime.SNMP.Generic': True,
        'N.Cpu.SNMP.HrProcessorLoad': True,
        'N.Memory.SNMP.NetSnmpReal': True,
        'N.AssetInventory.Snmp.Generic': True,
        'N.Topology_Layer3.SNMP.ipNetToMedia': False,
        'N.Routing.SNMP.Ipv4CidrRoutingTable': False
    }

    pollers = []
    for k in pollers_enabled:
        pollers.append(
            {
                'PollerType': k,
                'NetObject': 'N:' + nodeid,
                'NetObjectType': 'N',
                'NetObjectID': nodeid,
                'Enabled': pollers_enabled[k]
            }
        )

    for poller in pollers:
        print("  Adding poller type: {} with status {}... ".format(poller['PollerType'], poller['Enabled']), end="")
        response = client.create('Orion.Pollers', **poller)
        print("DONE!")

if __name__== '__main__':
    base_url = "https://62.12.150.162:10000/api/v2/"
    ncm_server = "sup-ncm-001.sdmz.umb.ch"
    ncm_username = "api-write"
    ncm_password = "Test12345678!"
    ncm_community = "umbmonitoring"

    # Logon to FortiGate first
    session = FortiGateAPI_logon(base_url)

    # read all the Access-Points
    FortiGateAPI_readAP(session)

    # Logon to NCM
    client = NCM_logon(ncm_server,ncm_username,ncm_password)
    #NCM_createNode(client,"10.230.220.36",ncm_community)

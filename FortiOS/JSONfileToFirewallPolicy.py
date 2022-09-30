""" Generate FortiGate Firewall Policies based on a JSON File
This script generate FortiGate Firewall Policies with the linked address
and service objects.
Connection to FortiGate works over the API connection.
The input file fromat is based on json (use the template file)

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
# __credits__ = ["None"]
__date__ = "2022/09/21"
__deprecated__ = False
__email__ = "ofee42@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.2"

####################
# Importer
####################
import getpass
import requests
import json
import urllib3

####################
# Init's
####################
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
BASE_URL = ""


####################
# Functions
####################

def create_objects(json_file, access_token):
    # Loop through all JSON objects
    for rule in json_file:
        for src in rule['src']:
            fgt_create_address(src['ip'], src['desc'], rule['vdom'], access_token)
        for dst in rule['dst']:
            fgt_create_address(dst['ip'], dst['desc'], rule['vdom'], access_token)

        for port in rule['ports']:
            fgt_create_service(port, rule['vdom'], access_token)

        rule_id = fgt_create_policy(rule, rule['vdom'], access_token)

        # Check if new Policy has to moved
        if isinstance(rule['after_policy'], int) or isinstance(rule['before_policy'], int):
            # Move after
            fgt_move_policy(rule, rule_id,  access_token)

def import_json():
    # Open JSON File from same folder
    with open('JSONfile_rules.json') as json_file:
        data = json.load(json_file)

    return data


def fgt_move_policy(rule, rule_id, access_token):
    move_url = ""
    # If "after_policy" is set, move Policy
    if isinstance(rule['after_policy'], int):
        move_url = "cmdb/firewall/policy/{0}?vdom={1}&action=move&after={2}&access_token={3}".format(rule_id, rule['vdom'], rule['after_policy'], access_token)

    if isinstance(rule['before_policy'], int):
        move_url = "cmdb/firewall/policy/{0}?vdom={1}&action=move&before={2}&access_token={3}".format(rule_id, rule['vdom'], rule['before_policy'], access_token)

    if move_url != "":
        url = BASE_URL + move_url
        res = requests.put(url, json={}, verify=False)

        if res.status_code == 200:
            print("Policy '{0}' moved.".format(rule['name']))
        else:
            response_data = json.loads(res.text)
            print("Error moving Policy: {0}".format(response_data.get('cli_error')))
            return False


def fgt_create_policy(rule, vdom, access_token):

    srcadr = []
    dstadr = []
    services = []

    for src in rule['src']:
        if "/" in src['ip']:
            srcadr.append({
                "name": "net_"+src['ip']
            })
        else:
            srcadr.append({
                "name": "host_" + src['ip']
            })

    for dst in rule['dst']:
        if "/" in dst['ip']:
            dstadr.append({
                "name": "net_" + dst['ip']
            })
        else:
            dstadr.append({
                "name": "host_" + dst['ip']
            })

    for port in rule['ports']:
        services.append({
            "name": port
        })


    payload = {
        "name": rule['name'],
        "status": "enable",
        "srcintf": [{"name": rule['src_int']}],
        "dstintf": [{"name": rule['dst_int']}],
        "action": "accept",
        "srcaddr": srcadr,
        "dstaddr": dstadr,
        "schedule": "always",
        "logtraffic": rule['logtraffic'],
        "nat": rule['nat'],
        "service": services,
        "comments": rule['desc']
    }

    url = BASE_URL + "cmdb/firewall/policy?vdom={0}&access_token={1}".format(vdom, access_token)
    res = requests.post(url, json=payload, verify=False)
    if res.status_code == 200:
        print("Policy '{0}' created.".format(rule['name']))

        response_data = json.loads(res.text)
        pol_id = response_data.get('mkey')
        return pol_id
    else:
        response_data = json.loads(res.text)
        print("Error Adding Policy: {0}".format(response_data.get('cli_error')))
        return False


def fgt_create_service(srv_name, vdom, access_token):
    if "_" not in srv_name:
        # Maybe is a Service Group - exit
        print("Error: no _ in service {0} found - abort.").format(srv_name)
        return

    # Split in to proto and port
    parts = srv_name.split("_")
    proto = parts[0]
    port = parts[1]

    if proto not in ['tcp', 'udp']:
        print("Error: no TCP oder UDP Proto in Service {0} - abort.".format(srv_name))
        return

    if "tcp" in proto:
        payload = {
            "name": srv_name,
            "protocol": proto,
            "tcp-portrange": port
        }
    elif "udp" in proto:
        payload = {
            "name": srv_name,
            "protocol": proto,
            "udp-portrange": port
        }

    url = BASE_URL + "cmdb/firewall.service/custom?vdom={0}&access_token={1}".format(vdom, access_token)
    res = requests.post(url, json=payload, verify=False)
    if res.status_code == 200:
        print("Service {0} created.".format(srv_name))
    else:
        print("Error 500: May Service {0} already exist!".format(srv_name))


def fgt_create_address(ip, description, vdom, access_token):
    if "/" in ip:
        # IP is subnet
        name = "net_{0}".format(ip)
        net = ip
        is_net = True
    else:
        name = "host_{0}".format(ip)
        net = "{0}/32".format(ip)
        is_net = False

    payload = {
        'name': name,
        'type': 'ipmask',
        'subnet': net,
        'description': description
    }

    url = BASE_URL + "cmdb/firewall/address?vdom={0}&access_token={1}".format(vdom, access_token)
    res = requests.post(url, json=payload, verify=False)
    if res.status_code == 200:
        print("Address {0} created.".format(name))
    else:
        print("Error 500: May Address {0} already exist!".format(name))


def fgt_login(fgt_username, fgt_password):
    payload = {'username': fgt_username, 'secretkey': fgt_password}
    url_login = BASE_URL + "authentication"

    # Start Session to keep cookies
    sess = requests.session()

    res = sess.post(url_login, json=payload, verify=False)

    # Read CSRFTOKEN and add it to the Header
    for cookie in sess.cookies:
        if 'ccsrftoken' in cookie.name:
            csrftoken = cookie.value[1:-1]
            sess.headers.update({'X-CSRFTOKEN': csrftoken})

    return sess


def main():
    # Ask for needed informations
    fgt_ip = str(input('FortiGate IP-Address (without Port):'))
    fgt_port = int(input('FortiGate HTTPS Port:'))
    fgt_accesstoken = str(input('FortiGate API Key:'))

    # Change global Variable
    global BASE_URL
    BASE_URL = "https://{0}:{1}/api/v2/".format(fgt_ip, fgt_port)

    # Import Rule
    json = import_json()
    create_objects(json, fgt_accesstoken)


if __name__ == '__main__':
    main()
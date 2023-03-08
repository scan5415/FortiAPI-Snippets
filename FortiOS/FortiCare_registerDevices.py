""" Register Fortinet Devices on FortiCare based on JSON file.
This script register the device on the Fortinet Support portal and activate the contract. For this all devices
need to be added in JSON file (Serialnumber, Contract Nr., Devicename as minimum)

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
__copyright__ = "Copyright 2023, Andy Scherer"
# __credits__ = ["None"]
__date__ = "2023/03/07"
__deprecated__ = False
__email__ = "ofee42@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.1"

import traceback

from FortiCare import FortiCare
import csv
import logging

logging.getLogger().addHandler(logging.StreamHandler())

# Start FortiCare Registration
api_user = input("FortiCare API Username")
api_password = input("FortiCare API Password")

forticare = FortiCare(api_user, api_password)

# Open File with Device details
with open('FortiCare-Devices.csv') as csvfile:
  csvreader = csv.DictReader(csvfile)
  for device in csvreader:
    try:
      device = dict(device)
      if len(device['SerialNumber']) > 1 and device['Registered'] != 'TRUE':
        payload = {
          "SerialNumber": device['SerialNumber'],
          "ContractNumber": device['ContractNumber'],
          "description": device['description']
        }

        res_code, res_msg = forticare.register_device(payload)
        if res_code == 200:
          print("{}({}) - SUCCESS - Device registered - Contract Expire: {}".format(device['description'], device['assets'][0]['serialNumber'], device['assets'][0]['contractTerms']['endDate']))
        else:
          print("{} - ERROR - {}".format(device['description'], res_msg))
    except Exception as e:
      logging.error(traceback.format_exc())


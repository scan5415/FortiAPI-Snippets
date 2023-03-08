""" This module is used for contacting Fortinet Support API Endpoints

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

####################
# Importer
####################
import requests, json, re
import logging
import pprint


####################
# Exceptions
####################


class FCBaseException(Exception):
  """Wrapper to catch the unexpected"""

  def __init__(self, msg):
    super(FCBaseException, self).__init__(msg)


class FCStatusException(FCBaseException):
  def __init__(self, status, m, fullResponse):
    msg = "Wrong status after request:\n- Status: {}\n- Message: {}".format(status, m)
    super(FCStatusException, self).__init__(msg)
    self._fullResponse = fullResponse

  def fullResponse(self):
    return self._fullResponse


####################
# Functions / Classes
####################

class Device(object):
  """
  Device parameteters
  """

  def __init__(self, serial_number, contract_number, description, gov=False):
    '''
    Create an asset class
    '''
    self._serialNumber = serial_number
    self._contractNumber = contract_number
    self._description = description
    self._gov = gov

  @property
  def serial_number(self):
    return self._serialNumber

  @property
  def contract_number(self):
    return self._contractNumber

  @property
  def description(self):
    return self._description

  @property
  def gov(self):
    return self._gov


class FortiCare():
  """
  Main class to interract with support.fortinet.com API
  """
  resourceBase = "ES/api/registration/v3/"

  maxBatchRegister = 10

  def __init__(self, user, password):
    self._user = user
    self._password = password
    self._baseUrl = 'https://support.fortinet.com'
    self._reqUrl = "{}/{}".format(self._baseUrl, self.resourceBase)
    self._access_token = ''

    # Login to FortiCare
    self._get_access_token()

  def __enter__(self):
    return self

  def __exit__(self, exc_type, exc_value, exc_traceback):
    if exc_type:
      print(f'exc_type: {exc_type}')
      print(f'exc_value: {exc_value}')
      # print(f'exc_traceback: {exc_traceback}')

  @property
  def access_token(self):
    return self._access_token

  def _get_access_token(self):
    payload = {
      "username": self._user,
      "password": self._password,
      "client_id": "assetmanagement",
      "grant_type": "password"
    }
    logging.debug("Payload is: {}".format(json.dumps(payload)))

    r = requests.post("https://customerapiauth.fortinet.com/api/v1/oauth/token/", json=payload)
    logging.debug("FortiCare login result is {}".format(r.json()['message']))
    logging.debug("JSON output is: {}".format(json.dumps(r.json(), indent=4)))

    self._access_token = r.json()["access_token"]

    return True

  def _send_request(self, rest_function, **kwargs):
    s = requests.session()
    headers = {"Authorization": "Baerer {}".format(self.access_token)}

    r = s.post("{}/{}".format(self._reqUrl, rest_function), **kwargs, headers=headers)

    if kwargs['json']:
      logging.debug("API request:\n%s", pprint.pformat(kwargs['json']))

    response = r.json()
    if r.status_code == 200:

      logging.debug("API response:\n%s", pprint.pformat(response))

      if not response['status'] == 0:
        return response['status'], response['message']
      else:
        return 200, response

    elif r.status_code == 400:
      return response['status'], response['message'] + " - May, Device or Contract already registered"
    else:
      raise FCStatusException(response['errors'][0]['code'], response['errors'][0]['message'], response)

  def register_device(self, device):
    """
    Register Device on FortiCare Portal
    :param device: JSON Object with parameters for API Request (see FortiCare API documentation for details)
    :return:
    """
    payload = {}
    payload['registrationUnits'] = []
    payload['registrationUnits'].append(device)
    logging.debug("payload: {}".format(json.dumps(payload)))

    res_code, res_msg = self._send_request("products/register", json=payload)
    return res_code, res_msg


""" This script check open Ports on a IP-Range. Initial written to check the
FortiGate Admin Web GUI. Actually, it can used for anything else.

Enter IPv4-Address or IPv4-Subnet with CIDR Prefix notation.
Currently, only IPv4 Addresses are supported.

REQUIREMENTS:
- pyfiglet


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
__date__ = "2022/10/06"
__deprecated__ = False
__email__ = "ofee42@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.1"

import socket

####################
# Importer
####################
import pyfiglet
import ipaddress
import time
import sys

####################
# Init's
####################
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


ADMIN_PORTS = ["444", "844", "10000"]


def test_predefined():
    ips = ["178.249.80.68",
           "212.243.90.20"]

    for ip in ips:
        test_port(ip)


def test_port(dst_ips):
    for ip in ipaddress.IPv4Network(dst_ips):
        str_ip = str(ip)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)

        # returns an error indicator
        print("Checking {0} ...".format(str_ip))

        for port in ADMIN_PORTS:
            result = s.connect_ex((str_ip, int(port)))
            if result == 0:
                print(f"{bcolors.FAIL}Port {port} at {str_ip} is open!{bcolors.ENDC}".format(port, str_ip))

            s.close()


def main():
    # Show Banner
    ascii_banner = pyfiglet.figlet_format("ADMIN GUI CHECKER")
    print(ascii_banner)
    print("-" * 50)

    # Do Port Check
    print("Start checking IPs...")

    test_predefined()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n Exiting Program !!!!")
        sys.exit()
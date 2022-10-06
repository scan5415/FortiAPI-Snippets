""" This script check open Ports on a IP-Range. Initial written to check the
FortiGate Admin Web GUI. Actually, it can used for anything else.

Enter IPv4-Address or IPv4-Subnet with CIDR Prefix notation.
Currently, only IPv4 Addresses are supported.

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


def test_port(dst_ips, fgt_port):

    for ip in ipaddress.IPv4Network(dst_ips):
        str_ip = str(ip)
        target = socket.gethostbyname(str(ip))
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket.setdefaulttimeout(1)

        # returns an error indicator
        print("Checking {0} ...".format(str_ip), end="\r")
        result = s.connect_ex((str_ip, int(fgt_port)))
        if result == 0:
            print(f"{bcolors.FAIL}Port {fgt_port} at {str_ip} is open!{bcolors.ENDC}".format(fgt_port, str_ip))
        s.close()


def main():
    # Show Banner
    ascii_banner = pyfiglet.figlet_format("ADMIN GUI CHECKER")
    print(ascii_banner)
    print("-" * 50)

    # Ask for needed informations
    dst_ips = str(input('To Scan IPv4-Subnet (e.g. 192.168.0.0/24:'))
    fgt_port = str(input('FortiGate Admin Port:'))

    # Do Port Check
    test_port(dst_ips, fgt_port)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n Exiting Program !!!!")
        sys.exit()
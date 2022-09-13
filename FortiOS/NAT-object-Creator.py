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
__date__ = "2022/05/30"
__deprecated__ = False
__email__ =  "ofee42@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Development"
__version__ = "0.0.1"

####################
# Importer
####################
import tkinter as tk
from tkinter import filedialog
from string import Template

####################
# Init's
####################

# Windows dialog init
root = tk.Tk()
root.withdraw()


# CLI Template
temp_vip = """edit vip_$externalIP
        set extip $externalIP
        set mappedip $internalIP
        set extintf $externalIntf
        set comment "$comment"
    next
"""
temp_base = """config firewall vip
    $entries
end
"""
####################
# Script START
####################
# Select File for input
print("Select txt file:")
file_path = filedialog.askopenfilename()


# Ask for external Interface
extInt = input("Set external Interface (e.g. port3): ")

cli_entries = ""
with open(file_path, "r") as filestream:
    for line in filestream:
        line.strip()
        currentline = line.split("\t")
        IPnat = currentline[0]
        IPorg = currentline[1]
        comment = currentline[2]

        cli_object = Template(temp_vip)
        cli_output = cli_object.substitute(externalIP=currentline[0], internalIP=currentline[1], comment=currentline[2], externalIntf=extInt)
        cli_entries = cli_entries + cli_output

# Add Base Template to CLI output
cli_command = Template(temp_base).substitute(entries=cli_entries)

# Save CLI to Textfile
save_file = filedialog.asksaveasfile(filetypes = [('Text Document', '*.txt')], defaultextension = [('Text Document', '*.txt')])
save_file.write(cli_command)
save_file.close()
print("NAT Objects created and saved in File. Enjoy!")

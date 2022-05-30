# FortiAPI-Snippets

## Get Switch Ports
### Requirement
- Installed python3 on your machine

### Needed python modules
Install the following python modules
- requests


### How to use
1. Download or Fork the script
2. Add the correct IP address, Username and Password in the script
3. Run it
4. check the outcome CSV files

HINT: The CSV files are saved to the running path of the script.

## FortiEMS-Endpoint
### Requirement
- Installed python3 on your machine

### Needed python modules
Install the following python modules
- requests


### How to use
1. Download or Fork the script
2. Add the correct IP address, Username and Password in the script
3. Run it
4. check the outcome CSV files

HINT: The CSV files are saved to the running path of the script.

## FortiGate Virtual-IP Object Generator
### Requirement
- Install python3 on your machine
- MacOS and Linux need additional Package (https://realpython.com/python-gui-tkinter/#building-your-first-python-gui-application-with-tkinter)

### How to use
1. Create a Textfile with coma separated values with following format
<external IP> <mapped IP> <comment>
2. Run the script
3. Select the previous generated file
4. Enter the external Interface
5. Save the export file
6. Open the generated file and copy & past the commands to your FortiGate

import requests
import json
import urllib3
import csv
import os
import yaml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

yaml_path = os.path.dirname(__file__)

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

def userInput():
    print("FortiEMS URL (e.g. https://ems.xx.ltd):")
    base_url = input()
    print("FortiEMS Username:")
    username = input()
    print("FortiEMS Password:")
    password = input()

    base_url = base_url + "/api/v1/"

    return base_url, username, password

def connectEMS(username, password):
    #Login request
    payload = {'name' : username, 'password' : password}
    res = requests.request("POST",url=url_login, json=payload, verify=False )

    print(res.json()['result']['message'])

    csrftoken = res.cookies['csrftoken']
    sessionid = res.cookies['sessionid']

    return csrftoken, sessionid

def loadYAML():
    with open(yaml_path + "/UMBconfigurator.yaml",'r') as stream:
        try:
            parsed_yaml=yaml.safe_load(stream)
            return parsed_yaml
        except yaml.YAMLError as exc:
            print(exc)

def formatResponse(res):
    if(res.json()['result']['retval'] == -1):
        print(bcolors.WARNING + res.json()['result']['message'] + bcolors.ENDC)
    elif(res.json()['result']['retval'] == -2):
        print(bcolors.FAIL + res.json()['result']['message'] + bcolors.ENDC)
    else:
        print(bcolors.OKGREEN + res.json()['result']['message'] + bcolors.ENDC)


def createProfile(type, settings):
    headers = {'Content-Type': "application/json", 'Referer': base_url, 'Cookie': "csrftoken=" + csrftoken + ";sessionid=" + sessionid, 'X-CSRFToken': csrftoken}

    res = requests.request("POST", url=base_url + "profiles/"+type+"/create", headers=headers, json=settings, verify=False)

    formatResponse(res)

def createZTNA_Tag(settings):
    headers = {'Content-Type': "application/json", 'Referer': base_url, 'Cookie': "csrftoken=" + csrftoken + ";sessionid=" + sessionid, 'X-CSRFToken': csrftoken}

    res = requests.request("POST", url=base_url + "/tags/zero_trust/create", headers=headers, json=settings, verify=False)

    formatResponse(res)

def createZTNA_Rule(settings):
    headers = {'Content-Type': "application/json", 'Referer': base_url, 'Cookie': "csrftoken=" + csrftoken + ";sessionid=" + sessionid, 'X-CSRFToken': csrftoken}

    res = requests.request("POST", url=base_url + "/tag_rules/zero_trust/create", headers=headers, json=settings, verify=False)

    print(res.json())
    formatResponse(res)


# GLOBAL Parameters
base_url, username, password = userInput()
url_login= base_url + "auth/signin"
csrftoken, sessionid = connectEMS(username, password)

# Load ConfigFile
settings = loadYAML()

# Push Settings to FortiEMS
print(bcolors.BOLD + "LOG: Start importing VPN Profiles..." + bcolors.ENDC)
for profile in settings['profiles']['vpn']:
    createProfile('vpn', profile)
print(bcolors.BOLD + "LOG: Imported VPN Profiles..." + bcolors.ENDC)

print(bcolors.BOLD + "LOG: Start importing ZTNA Profiles..." + bcolors.ENDC)
for profile in settings['profiles']['ztna']:
    createProfile('ztna', profile)
print(bcolors.BOLD + "LOG: Imported ZTNA Profiles..." + bcolors.ENDC)

print(bcolors.BOLD + "LOG: Start importing Webprofile..." + bcolors.ENDC)
for profile in settings['profiles']['web']:
    createProfile('webfilter', profile)
print(bcolors.BOLD + "LOG: Imported Webprofiles..." + bcolors.ENDC)

print(bcolors.BOLD + "LOG: Start importing Vulnerabilty Profiles..." + bcolors.ENDC)
for profile in settings['profiles']['vulnerability']:
    createProfile('vulnerability_scan', profile)
print(bcolors.BOLD + "LOG: Imported Vulnerabilty Profiles..." + bcolors.ENDC)

print(bcolors.BOLD + "LOG: Start importing Antivirus Profiles..." + bcolors.ENDC)
for profile in settings['profiles']['antivirus']:
    createProfile('malware', profile)
print(bcolors.BOLD + "LOG: Imported Malware Profiles..." + bcolors.ENDC)

print(bcolors.BOLD + "LOG: Start importing Sandbox Profiles..." + bcolors.ENDC)
for profile in settings['profiles']['sandbox']:
    createProfile('sandbox', profile)
print(bcolors.BOLD + "LOG: Imported Sandbox Profiles..." + bcolors.ENDC)

print(bcolors.BOLD + "LOG: Start importing Client Settings..." + bcolors.ENDC)
for profile in settings['profiles']['clientSettings']:
    createProfile('system', profile)
print(bcolors.BOLD + "LOG: Imported Client Settings..." + bcolors.ENDC)


# Push ZTNA Settings to FortiEMS
print(bcolors.BOLD + "LOG: Start importing ZTNA Tags..." + bcolors.ENDC)
for tag in settings['ztna']['tags']:
    createZTNA_Tag(tag)
print(bcolors.BOLD + "LOG: Imported ZTNA Tags..." + bcolors.ENDC)

#print(bcolors.BOLD + "LOG: Start importing ZTNA Rules..." + bcolors.ENDC)
#for rule in settings['ztna']['rules']:
#    createZTNA_Rule(rule)
#print(bcolors.BOLD + "LOG: Imported ZTNA Rules..." + bcolors.ENDC)

import json
import argparse
import csv
from pathlib import Path
from rich.table import Table
from rich.console import Console

def extract_devices(root):
    devices = []

    def add_device(d):
        # ensure it's a dict and copy so we can add/override fields
        if isinstance(d, dict):
            devices.append(dict(d))

    # handle top-level result array
    if isinstance(root, dict):
        for r in root.get("result", []):
            data = r.get("data")

            # case: data is a dict with dynamic_mapping (FortiManager style)
            if isinstance(data, dict) and "dynamic_mapping" in data:
                for mapping in data.get("dynamic_mapping", []):
                    value = mapping.get("value", "")
                    # mapping might contain explicit dns keys
                    for scope in mapping.get("_scope", []):
                        devicename = scope.get("name") or scope.get("device") or ""
                        # prefer explicit dns keys in mapping, fall back to mapping.value
                        dns_server1 = value if r.get("url", "").__contains__("dns_primary") else None
                        dns_server2 = value if r.get("url", "").__contains__("dns_secondary") else None

                        # Check if device already exists
                        found = False
                        for existing in devices:
                            if existing.get("devicename") == devicename:
                                if dns_server1 is not None:
                                    existing["fmg_dns1"] = dns_server1
                                if dns_server2 is not None:
                                    existing["fmg_dns2"] = dns_server2
                                found = True
                                break
                        if not found:
                            dev = {"devicename": devicename}
                            if dns_server1 is not None:
                                dev["fmg_dns1"] = dns_server1
                            if dns_server2 is not None:
                                dev["fmg_dns2"] = dns_server2
                            devices.append(dev)

            # case: data is a list of device dicts
            elif isinstance(data, list):
                for item in data:
                    add_device(item)

            # case: data is a dict that itself contains "data": [...]
            elif isinstance(data, dict) and isinstance(data.get("data"), list):
                for item in data["data"]:
                    add_device(item)

            # unexpected shapes: if r is a dict with device-like keys, add it
            elif isinstance(r, dict) and ( "devicename" in r or "name" in r or "data" not in r):
                add_device(r)

    # fallback: root itself might be a list or contain "data" list
    if not devices:
        if isinstance(root, list):
            for item in root:
                add_device(item)
        elif isinstance(root, dict):
            if isinstance(root.get("data"), list):
                for item in root["data"]:
                    add_device(item)

    return devices

def normalize_dns(item):
    fmg_dns1 = (
        item.get("fmg_dns1")
        or item.get("dns")
        or ""
    )
    fmg_dns2 = (
        item.get("fmg_dns2")
        or ""
    )
    list_dns1 = (
        item.get("list_dns1")
        or item.get("dns")
        or ""
    )
    list_dns2 = (
        item.get("list_dns2")
        or ""
    )
    compare = False
    if fmg_dns1 == list_dns1 and fmg_dns2 == list_dns2:
        compare = True

    if compare:
        return True, True, True, True, compare
    else:
        return fmg_dns1, fmg_dns2, list_dns1, list_dns2, compare

def update_devices_with_csv(devices, csv_path):
    if not csv_path.exists():
        return
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sas = (row.get('SAS-Code') or '').strip()
            dns_primary = (row.get('Perimeter VDOM DNS Server primary') or '').strip()
            dns_secondary = (row.get('Perimeter VDOM DNS Server secondary') or '').strip()
            for device in devices:
                if sas.lower() in device.get("devicename"):
                    if dns_primary:
                        device["list_dns1"] = dns_primary
                    if dns_secondary:
                        device["list_dns2"] = dns_secondary
                    break


def main():
    filename = Path(__file__).parent / "fmg-api.json"
    csv_path = Path(__file__).parent / "Locationlist.csv"

    with open(filename, "r") as f:
        data = json.load(f)

    devices = extract_devices(data)

    # Update devices with DNS info from CSV
    update_devices_with_csv(devices, csv_path)

    table = Table(title="Devices DNS")
    table.add_column("devicename", style="cyan")
    table.add_column("Manager DNS Primary", style="green")
    table.add_column("Manager DNS Secondary", style="green")
    table.add_column("Excel DNS Primary", style="yellow")
    table.add_column("Excel DNS Secondary", style="yellow")
    table.add_column("Compare", style="red")

    for d in devices:
        name = d.get("devicename") or d.get("name") or d.get("device") or ""
        fmg_dns1, fmg_dns2, list_dns1, list_dns2, compare = normalize_dns(d)
        if not compare: # IPs are not matching, list in the table
            table.add_row(name, fmg_dns1, fmg_dns2, list_dns1, list_dns2, compare and "Match" or "Mismatch")

    Console().print(table)

if __name__ == "__main__":
    main()
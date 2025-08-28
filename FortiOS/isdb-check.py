import json
import requests
from rich import print
from rich.table import Table
from rich.console import Console
from rich.prompt import Prompt
from ipaddress import ip_network

# Variables for API access
API_KEY = "repace-with-your-api-key"
BASE_URL = "https://replace-with-your-ip:10000/api/v2"
rich_con = Console()


def fortigate_get(endpoint: str, params: dict = None):
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params, verify=False)
    return response

def read_ips_from_file(filename: str):
    with rich_con.status("[bold green]Reading all IPs...") as status:
        ips = []
        with open(filename, "r") as f:
            counter = 0
            for lines in f:
                

                for line in lines.split(","):
                    line = line.strip()

                    if not line or line.startswith("#"):
                        continue
                    try:
                        # Check if it's a range or single IP
                        net = ip_network(line, strict=False)

                        counter += 1
                        ips.append(str(net))

                    except ValueError:
                        counter += 1
                        ips.append(str(ip))

                    status.update(f"[bold green]Reading all ({counter}) IPs...[/bold green]")
    return ips

def main(ip_file: str):
    # Read all IPs from file
    src_ips = read_ips_from_file(ip_file)

    # Used ISDB objects in Firewall policies
    used_isdbs = [
        "Microsoft-Intune",
        "Microsoft-Azure",
        "Microsoft-FTP",
        "Microsoft-Other",
        "Microsoft-Office365",
        "Microsoft-Skype_Teams",
        "Microsoft-Outlook"
    ]

    # Create a table for results
    table = Table(title="FortiGate Internet Service Match Results")
    table.add_column("IP Address", style="cyan")
    table.add_column("ISDB Match in policy objects", style="magenta")


    # Ask for IP to check, or check all IPs from file
    str_ip = Prompt.ask("Enter an IP address to check (or press Enter to check all IPs from file)", default="")
    if str_ip:
        # Validate the input IP address
        try:
            target_ip = str(ip_network(str_ip, strict=False))
            target_ips = [target_ip]
        except ValueError:
            rich_con.print(f"[bold red]Invalid IP address: {str_ip}[/bold red]")
            return

        # Add special column to table
        table.add_column("IP matches ISDB", style="magenta")
        table.add_column("On MS Website", style="green")

        # Check if the IP is in the list
        is_matching = False
        for src_ip in src_ips:
            if ip_network(src_ip, strict=False).overlaps(ip_network(target_ip, strict=False)):
                is_matching = True
                break
        
        # Check the ISDB objects from API
        isdb_matching, isdb_all = check_fgt_isdb(target_ip, used_isdbs)

        # Check if the target IP matches any of the used IPs in file
        if is_matching:
            table.add_row(target_ip, isdb_matching, isdb_all, "OK")
        else:
            table.add_row(target_ip, isdb_matching, isdb_all, "NOT MATCHING!")
    else:
        
        counter = 0

        with rich_con.status("[bold green]Checking all IPs...") as status:
            for ip in src_ips:
                isdb_matching, isdb_all = check_fgt_isdb(ip, used_isdbs)

                counter += 1
                status.update(f"[bold green]Checking all ({counter}) IPs...[/bold green]")
                
                table.add_row(ip, isdb_matching)

    print(table)


def check_fgt_isdb(ip: str, used_isdbs: list):
    endpoint = f"/monitor/firewall/internet-service-match"
    net = ip_network(ip, strict=False)
    params = {"ip": net.network_address, "is_ipv6": "false", "ipv4_mask": net.netmask}
    response = fortigate_get(endpoint, params)
                
    if response.status_code == 200:
        obj_results = json.loads(response.text) 
        if len(used_isdbs) > 0:
            matching_isdb = [
                item.get("name", "")
                for item in obj_results.get("results", [])
                if item.get("name", "") in used_isdbs
            ]
        else:
            matching_isdb = []
        
        # Get all ISDB names
        all_isdb = [
            item.get("name", "")
            for item in obj_results.get("results", [])
            ]
        return "\n".join(matching_isdb) if len(matching_isdb) > 0 else "NOT MATCHING!", "\n".join(all_isdb) if len(all_isdb) > 0 else "NOT MATCHING!"
    else:
        return {"error": "Failed to retrieve data"}
    
        
if __name__ == "__main__":
    # Replace 'ips.txt' with your actual file name
    main("ips-china.txt")
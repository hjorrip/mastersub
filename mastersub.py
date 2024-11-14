import re
import requests
import sys
import xml.etree.ElementTree as ET
import subprocess
import os

def get_tenant_domains(domain):
    url = "https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc"

    data = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:exm="http://schemas.microsoft.com/exchange/services/2006/messages"
               xmlns:ext="http://schemas.microsoft.com/exchange/services/2006/types"
               xmlns:a="http://www.w3.org/2005/08/addressing"
               xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Header>
        <a:Action soap:mustUnderstand="1">http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation</a:Action>
        <a:To soap:mustUnderstand="1">https://autodiscover-s.outlook.com/autodiscover/autodiscover.svc</a:To>
        <a:ReplyTo>
            <a:Address>http://www.w3.org/2005/08/addressing/anonymous</a:Address>
        </a:ReplyTo>
    </soap:Header>
    <soap:Body>
        <GetFederationInformationRequestMessage xmlns="http://schemas.microsoft.com/exchange/2010/Autodiscover">
            <Request>
                <Domain>{domain}</Domain>
            </Request>
        </GetFederationInformationRequestMessage>
    </soap:Body>
</soap:Envelope>"""

    headers = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPAction": '"http://schemas.microsoft.com/exchange/2010/Autodiscover/Autodiscover/GetFederationInformation"',
        "User-Agent": "AutodiscoverClient",
    }

    print(f"Retrieving tenant domains for {domain}...")
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to the server: {e}")
        return []

    if response.status_code != 200:
        print(f"Error: HTTP {response.status_code}")
        return []

    # Parse the XML response
    try:
        namespaces = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'a': 'http://www.w3.org/2005/08/addressing',
            'm': 'http://schemas.microsoft.com/exchange/2010/Autodiscover',
            'autodiscover': 'http://schemas.microsoft.com/exchange/2010/Autodiscover',
        }
        root = ET.fromstring(response.content)

        # Check for errors
        error = root.find('.//m:ErrorCode', namespaces)
        if error is not None and error.text != 'NoError':
            print(f"Error from server: {error.text}")
            return []

        # Extract domains
        domains = []
        for domain_elem in root.findall('.//autodiscover:Domain', namespaces):
            domains.append(domain_elem.text)

        return domains
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return []

def select_domains(domains):
    from questionary import checkbox

    print("\nPlease select the domains for the next step:")
    choices = []
    for domain_info in domains:
        domain = domain_info['domain']
        discovered_from = domain_info['discovered_from']
        # Build display name
        if discovered_from:
            display_name = f"{domain} (discovered from {discovered_from})"
        else:
            display_name = f"{domain} (initial domain)"
        checked = not domain.endswith('.onmicrosoft.com')
        choices.append({'name': display_name, 'value': domain, 'checked': checked})

    selected_domains = checkbox(
        "Select domains (use space to toggle selection, up/down to navigate):",
        choices=choices
    ).ask()

    if selected_domains is None:
        print("No domains selected.")
        return []
    else:
        return selected_domains

def get_subdomains(api_key, domain):
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {
        "APIKEY": api_key,
        "accept": "application/json",
    }
    params = {
        "children_only": "false",
        "include_inactive": "true"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            subdomains = data.get("subdomains", [])
            subdomain_count = data.get("subdomain_count", len(subdomains))
            return subdomains, subdomain_count
        else:
            print(f"Error fetching subdomains for {domain}: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return [], 0
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to SecurityTrails API for {domain}: {e}")
        return [], 0

def run_httpx(input_file, output_file):
    # Run httpx on the subdomains and save the output to a file
    cmd = [
        'httpx',
        '-l', input_file,
        '-sc',
        '-title',
        '-server',
        '-efqdn',
        '-fc', '404',
        '-o', output_file
    ]
    print(f"Executing httpx command:\n{' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0:
            print(f"Error running httpx:\n{result.stdout}\n{result.stderr}")
            return False
        else:
            print("httpx command completed successfully.")
            return True
    except FileNotFoundError:
        print("Error: 'httpx' command not found. Please ensure httpx is installed and in your PATH.")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while running httpx: {e}")
        return False

def main():
    import argparse
    from questionary import text

    parser = argparse.ArgumentParser(description='Tenant Domain and Subdomain Discovery')
    parser.add_argument('domains', nargs='+', help='One or more domains to query')
    parser.add_argument('--apikey', required=True, help='SecurityTrails API Key')
    args = parser.parse_args()

    api_key = args.apikey.strip()

    # Initialize a dictionary to hold domain info
    all_domains = {}

    for domain in args.domains:
        print(f"Retrieving tenant domains for {domain}...")
        tenant_domains = get_tenant_domains(domain)
        if tenant_domains:
            print(f"\nDomains found for {domain}:")
            for d in tenant_domains:
                print(d)
                if d not in all_domains:
                    all_domains[d] = {'domain': d, 'discovered_from': domain}
        else:
            print(f"No domains found for {domain}.")
        # Always add the input domain to all_domains
        if domain not in all_domains:
            all_domains[domain] = {'domain': domain, 'discovered_from': None}
        else:
            # If domain is already in all_domains, and 'discovered_from' is not None, set it to None
            if all_domains[domain]['discovered_from'] is not None:
                all_domains[domain]['discovered_from'] = None

    if not all_domains:
        print("No domains to select.")
        sys.exit(0)

    # Convert the all_domains dictionary to a list for selection
    domain_list = list(all_domains.values())

    selected_domains = select_domains(domain_list)
    if not selected_domains:
        print("No domains selected.")
        sys.exit(0)

    print("\nSelected Domains:")
    for d in selected_domains:
        print(d)

    # Set default base filename based on the first selected domain
    default_base_filename = selected_domains[0].split('.')[0]

    # Ask for base filename/project name with default
    from questionary import prompt
    base_filename_question = [
        {
            'type': 'input',
            'name': 'base_filename',
            'message': f"\nEnter a base name for output files (default: '{default_base_filename}')",
            'default': default_base_filename
        }
    ]
    base_filename_answer = prompt(base_filename_question)
    base_filename = base_filename_answer.get('base_filename', default_base_filename)
    if not base_filename:
        base_filename = default_base_filename
        print(f"No base filename provided. Using default: {base_filename}")

    # Retrieve subdomains for each selected domain
    print("\nRetrieving subdomains from SecurityTrails...")
    all_subdomains = {}
    domain_subdomain_counts = []
    total_subdomains = 0
    total_live_subdomains = 0
    for domain in selected_domains:
        print(f"Processing domain: {domain}")
        subdomains, count = get_subdomains(api_key, domain)
        full_subdomains = [f"{subdomain}.{domain}" for subdomain in subdomains]  # Full subdomain names
        all_subdomains[domain] = full_subdomains
        domain_subdomain_counts.append({'domain': domain, 'subdomain_count': count})
        total_subdomains += count

    if not total_subdomains:
        print("No subdomains found for the selected domains.")
        sys.exit(0)

    # Save all subdomains to file
    all_subdomains_filename = f"{base_filename}-all.txt"
    try:
        print(f"\nSaving all subdomains to {all_subdomains_filename}...")
        with open(all_subdomains_filename, 'w') as f:
            for domain, subdomains in all_subdomains.items():
                for subdomain in subdomains:
                    f.write(f"{subdomain}\n")
        print(f"All subdomains saved to {all_subdomains_filename}")
    except IOError as e:
        print(f"Error saving all subdomains to file: {e}")
        sys.exit(1)

    # Run httpx on all subdomains and collect live domains
    live_subdomains_filename = f"{base_filename}-alive.txt"
    httpx_output_filename = f"{base_filename}-httpx.txt"
    print("\nRunning httpx on discovered subdomains...")
    httpx_success = run_httpx(all_subdomains_filename, httpx_output_filename)
    if not httpx_success:
        print("httpx did not run successfully. Exiting.")
        sys.exit(1)

    # Read httpx output and extract live subdomains
    print(f"Reading httpx output from {httpx_output_filename}...")
    live_subdomains = []
    try:
        with open(httpx_output_filename, 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.strip():
                    # Extract the URL (e.g., https://subdomain.example.com)
                    url = line.strip().split()[0]
                    # Remove the protocol to get the subdomain
                    subdomain = url.replace('http://', '').replace('https://', '').split('/')[0]
                    live_subdomains.append(subdomain)
        print(f"Found {len(live_subdomains)} live subdomains.")
    except IOError as e:
        print(f"Error reading httpx output file: {e}")
        sys.exit(1)

    # Save live subdomains to file
    try:
        print(f"Saving live subdomains to {live_subdomains_filename}...")
        with open(live_subdomains_filename, 'w') as f:
            for subdomain in live_subdomains:
                f.write(f"{subdomain}\n")
        print(f"Live subdomains saved to {live_subdomains_filename}")
    except IOError as e:
        print(f"Error saving live subdomains to file: {e}")
        sys.exit(1)

    # Update live subdomain counts
    live_subdomains_set = set(live_subdomains)
    for item in domain_subdomain_counts:
        domain = item['domain']
        subdomains = all_subdomains.get(domain, [])
        live_count = sum(1 for subdomain in subdomains if subdomain in live_subdomains_set)
        item['live_count'] = live_count
        total_live_subdomains += live_count

    # Print the table with headers and total count
    print("\nSubdomain Counts:")
    header = f"{'Domain':<30} {'Subdomains Found':>17} {'Live Subdomains':>17}"
    print(header)
    print("-" * len(header))
    for item in domain_subdomain_counts:
        domain = item['domain']
        count = item['subdomain_count']
        live_count = item.get('live_count', 0)
        print(f"{domain:<30} {count:>17} {live_count:>17}")
    print("-" * len(header))
    print(f"{'Total Subdomains':<30} {total_subdomains:>17} {total_live_subdomains:>17}")

if __name__ == "__main__":
    main()

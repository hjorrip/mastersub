
# MasterSub

MasterSub is a Python script for tenant domain and subdomain discovery. It retrieves tenant domains associated with a given domain, fetches subdomains using the SecurityTrails API, and identifies live subdomains using [`httpx`](https://github.com/projectdiscovery/httpx).

## Features

- **Tenant Domain Retrieval**: Discovers tenant domains via Microsoft's Autodiscover service.
- **Subdomain Enumeration**: Fetches subdomains for selected domains using the SecurityTrails API.
- **Live Subdomain Detection**: Identifies live subdomains by probing with `httpx`.
- **Output Files**: Saves all subdomains and live subdomains to separate files.
- **Summary Table**: Provides a summary table of subdomains found and live subdomains.

## Installation

### Prerequisites

- **Python 3.6** or higher
- **[`httpx`](https://github.com/projectdiscovery/httpx)** from ProjectDiscovery
- **SecurityTrails API Key**
- **Go Programming Language** (required to install `httpx`)

### Clone the Repository

```bash
git clone https://github.com/yourusername/mastersub.git
cd mastersub
```

### Install Python Dependencies

It's recommended to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Install `httpx`

Install `httpx` from ProjectDiscovery:

```bash
GO111MODULE=on go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
```

Ensure that the Go binary path is added to your `PATH` environment variable. You can add the following line to your `~/.bashrc` or `~/.bash_profile`:

```bash
export PATH=$PATH:$(go env GOPATH)/bin
```

Verify the installation by running:

```bash
httpx -version
```

### Obtain a SecurityTrails API Key

1. Sign up for a [SecurityTrails](https://securitytrails.com/) account if you don't have one.
2. Navigate to your account settings to obtain your API key.

## Usage

Run the script with one or more domains and your SecurityTrails API key:

```bash
python discover_subdomains.py example.com --apikey YOUR_API_KEY
```

### Options

- `--apikey`: Your SecurityTrails API key (required).
- `domains`: One or more domains to query.

### Example

```bash
python discover_subdomains.py example.com --apikey YOUR_API_KEY
```

### Workflow

1. **Tenant Domain Retrieval**: The script retrieves tenant domains associated with the provided domain(s).
2. **Domain Selection**: You will be prompted to select which domains to proceed with. Domains ending with `.onmicrosoft.com` are deselected by default.
3. **Base Filename**: You will be prompted to enter a base name for the output files. A default is provided based on the first selected domain.
4. **Subdomain Retrieval**: The script fetches subdomains for the selected domains using the SecurityTrails API.
5. **Subdomain Probing**: It runs `httpx` to identify live subdomains.
6. **Results**:
   - All subdomains are saved to `<base_filename>-all.txt`.
   - Live subdomains are saved to `<base_filename>-alive.txt`.
   - A summary table is displayed.

## Sample Output

```plaintext
$ python discover_subdomains.py example.com --apikey YOUR_API_KEY

Retrieving tenant domains for example.com...

Domains found for example.com:
example.com
example.onmicrosoft.com

Please select the domains for the next step:
Select domains (use space to toggle selection, up/down to navigate):
 ◯ example.onmicrosoft.com
 ◉ example.com

Selected Domains:
example.com

Enter a base name for output files (default: 'example')
>  (Pressed Enter)

Retrieving subdomains from SecurityTrails...
Processing domain: example.com

Saving all subdomains to example-all.txt...
All subdomains saved to example-all.txt

Running httpx on discovered subdomains...
Executing httpx command:
httpx -l example-all.txt -sc -title -server -efqdn -fc 404 -o example-httpx.txt
httpx command completed successfully.

Reading httpx output from example-httpx.txt...
Found 15 live subdomains.
Saving live subdomains to example-alive.txt...
Live subdomains saved to example-alive.txt

Subdomain Counts:
Domain                          Subdomains Found   Live Subdomains
------------------------------------------------------------------
example.com                                  75                15
------------------------------------------------------------------
Total Subdomains                             75                15
```

## Notes

- **Dependencies**: The script relies on the `requests` and `questionary` Python packages.
- **HTTPX Options**: The script uses `httpx` with options to filter out 404 responses.
- **Performance**: Depending on the number of subdomains, the script may take some time to complete.
- **Legal**: Ensure you have proper authorization to perform scanning on the target domains.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Disclaimer

Use this tool responsibly and ensure you have permission to perform scanning on the target domains. Unauthorized scanning may be illegal in your jurisdiction.

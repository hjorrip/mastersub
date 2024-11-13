mastersub
mastersub is a Python script for discovering tenant domains and subdomains, leveraging SecurityTrails API and httpx. It automates the process of retrieving subdomains, checking for live hosts, and compiling the results.

Features
Retrieves tenant domains using Microsoft's Autodiscover service.
Fetches subdomains from SecurityTrails API.
Checks for live subdomains using httpx.
Outputs results in organized files:
All discovered subdomains.
Live subdomains identified by httpx.
Provides a summary table of subdomains found and live subdomains.
Installation
Prerequisites
Python 3.6+
SecurityTrails API Key: Obtain from your SecurityTrails account.
httpx: Install httpx from ProjectDiscovery.
Clone the Repository
bash
Copy code
git clone https://github.com/yourusername/mastersub.git
cd mastersub
Install Python Dependencies
It's recommended to use a virtual environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install the required Python packages:

bash
Copy code
pip install -r requirements.txt
Install httpx
Ensure you have Go installed and set up in your environment.

Install httpx using go:

bash
Copy code
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
Ensure that the httpx binary is in your system's PATH. You can typically find the installed binary in $HOME/go/bin or %USERPROFILE%\go\bin.

Add the following to your .bashrc, .zshrc, or equivalent:

bash
Copy code
export PATH=$PATH:$HOME/go/bin
Verify the installation:

bash
Copy code
httpx -version
You should see the version information of httpx.

Usage
Run the script with one or more domains and your SecurityTrails API key:

bash
Copy code
python discover_subdomains.py example.com --apikey YOUR_SECURITYTRAILS_API_KEY
Options
--apikey: (Required) Your SecurityTrails API Key.
domains: One or more domains to query.
Example
bash
Copy code
python discover_subdomains.py example.com --apikey YOUR_SECURITYTRAILS_API_KEY
Sample Output
vbnet
Copy code
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
>

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
example.com                                   75                15
------------------------------------------------------------------
Total Subdomains                              75                15
Output Files
<base_name>-all.txt: Contains all subdomains discovered via SecurityTrails.
<base_name>-alive.txt: Contains live subdomains identified by httpx.
<base_name>-httpx.txt: Contains the detailed output from httpx.
Notes
Deselected .onmicrosoft.com Domains: During the domain selection step, domains ending with .onmicrosoft.com are deselected by default.
Excluding 404 Responses: The script uses httpx with the -fc 404 option to filter out responses with a 404 status code, focusing on potentially active subdomains.
Customizing httpx Parameters: If you wish to adjust httpx parameters, you can modify the run_httpx function in the script.
Troubleshooting
httpx Command Not Found: Ensure that httpx is installed and the binary is in your system's PATH.
Permissions: Ensure you have the necessary permissions to read and write files in the directory.
Python Version: The script requires Python 3.6 or higher.
Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

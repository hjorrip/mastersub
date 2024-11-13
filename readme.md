
# MasterSub

MasterSub is a Python-based tool designed to fetch subdomains from SecurityTrails, analyze their activity using `httpx`, and provide a summarized table of results. It supports saving outputs to files for further processing.

## Features

- Fetch subdomains using SecurityTrails API.
- Check for live subdomains using `httpx`.
- Save results to customizable output files.
- Easy-to-use command-line interface.

## Installation

### Requirements

- Python 3.8 or higher
- SecurityTrails API Key
- `httpx` (from ProjectDiscovery)

### Install Python Dependencies

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/mastersub.git
   cd mastersub
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Install `httpx`

#### Using Precompiled Binary (Recommended)

1. **Download the Precompiled Binary**:
   - Visit [ProjectDiscovery HTTPX Releases](https://github.com/projectdiscovery/httpx/releases).
   - Download the binary for your operating system (e.g., Linux or macOS).

2. **Move Binary to PATH**:
   - After downloading, move the binary to a directory in your system's `PATH`. For example:
     ```bash
     mv httpx /usr/local/bin/
     chmod +x /usr/local/bin/httpx
     ```

3. **Verify Installation**:
   - Run the following command to confirm:
     ```bash
     httpx -version
     ```
   - You should see the version of `httpx` installed.

## Usage

1. Run the script:
   ```bash
   python mastersub.py --apikey <API_KEY> example.com
   ```

2. Enter the base name for output files when prompted (or press Enter for a default name).

3. Review subdomains found by SecurityTrails and select which to analyze.

4. Results:
   - `example-all.txt`: Contains all subdomains discovered.
   - `example-alive.txt`: Contains only the live subdomains.

## Example Output

### Subdomain Counts Table:
```
Subdomain Counts:
Domain                          Subdomains Found   Live Subdomains
------------------------------------------------------------------
example.com                                   75                 15
------------------------------------------------------------------
Total Subdomains                              75                 15
```

### File Outputs:
- `example-all.txt`:
  ```
  sub1.example.com
  sub2.example.com
  ...
  ```
- `example-alive.txt`:
  ```
  https://sub1.example.com [200] [nginx]
  https://sub2.example.com [403] [Apache]
  ...
  ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

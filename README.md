# DuckDNSUpdater.py

There are certainly more elegant ways to do this but this script will check your public IP every 5 minutes (default) and update DuckDNS through their HTTP/HTTPS API if a change is detected.

## Requirements

* Python 3.8 or newer
* A DuckDNS account
* An existing DuckDNS subdomain
* Your DuckDNS account token


## Instructions

Replace these values in the script with your DuckDNS information:

DUCKDNS_DOMAIN = "your-subdomain"

DUCKDNS_TOKEN = "your-duckdns-token"

After that just run the script.


Do not publish or share a copy of the script containing your token. Anyone with access to the token will be able to modify your DuckDNS DNS record.

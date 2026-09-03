import ipaddress
import logging
import time
import urllib.parse
import urllib.request

#config
DUCKDNS_DOMAIN = "" #Your DuckDNS domain name (without .duckdns.org)
DUCKDNS_TOKEN = "" #Your DuckDNS token
CHECK_INTERVAL = 300 #How often to check for public IP changes (in seconds).
IP_SERVICES = ["https://api.ipify.org", "https://checkip.amazonaws.com"] #This is just redundancy, the first one was acting inconsistent during testing idk.
DUCKDNS_URL = "https://www.duckdns.org/update" #This will literally never change, but if it does, you can change it here.

#console logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger("DuckDNS")

#ip change check
def get_public_ip(): #Will attempt to get current public IP from a list of services, returning the IPv4 as a string if successful, or None if not.
    for service in IP_SERVICES:
        try:
            request = urllib.request.Request(
                service,
                headers={
                    "User-Agent": "DuckDNS-IP-Monitor/1.0"
                },
            )
            with urllib.request.urlopen(
                request,
                timeout=10
            ) as response:
                ip = response.read().decode().strip()
            parsed_ip = ipaddress.ip_address(ip)
            if parsed_ip.version != 4:
                continue
            return ip
        except Exception:
            continue
    return None

#duckDNS update
def update_duckdns(ip): #Updates duckDNS with the IPv4 if a change is detected, returning True if successful, False otherwise.
    parameters = urllib.parse.urlencode(
        {
            "domains": DUCKDNS_DOMAIN,
            "token": DUCKDNS_TOKEN,
            "ip": ip,
            "verbose": "true",
        }
    )
    url = f"{DUCKDNS_URL}?{parameters}"
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "DuckDNS-IP-Monitor/1.0"
            },
        )
        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:
            result = response.read().decode().strip()
        if result.startswith("OK"):
            log.info(
                "DuckDNS successfully set to %s",
                ip,
            )
            return True
        log.error(
            "DuckDNS rejected the update: %s",
            result,
        )
    except Exception as error:
        log.error(
            "Could not reach DuckDNS: %s",
            error,
        )
    return False

#main loop
def main():
    log.info("DuckDNS IP monitor started.") #startup logging
    log.info(
        "Monitoring: %s.duckdns.org",
        DUCKDNS_DOMAIN,
    )
    log.info(
        "Checking every %d seconds.",
        CHECK_INTERVAL,
    )
    last_updated_ip = None
    internet_was_offline = False
    while True: #Check the IP and checking if we lost internet.
        try:
            current_ip = get_public_ip()
            if current_ip is None:
                if not internet_was_offline:
                    log.warning(
                        "Internet connection unavailable. "
                        "DuckDNS updates paused."
                    )
                    internet_was_offline = True
                time.sleep(CHECK_INTERVAL)
                continue
            if internet_was_offline:
                log.info(
                    "Internet connection restored."
                )
                internet_was_offline = False
            if last_updated_ip is None: #first run: sync DuckDNS with the current public IP
                log.info(
                    "Current public IP: %s",
                    current_ip,
                )
                log.info(
                    "Synchronizing DuckDNS..."
                )
                if update_duckdns(current_ip):
                    last_updated_ip = current_ip
            elif current_ip != last_updated_ip: #public IP changed: update DuckDNS and remember the new address
                log.info(
                    "Public IP changed: %s -> %s",
                    last_updated_ip,
                    current_ip,
                )
                if update_duckdns(current_ip):
                    last_updated_ip = current_ip
            else: #Nothing changed, just log it and wait for the next check.
                log.info(
                    "Public IP unchanged: %s",
                    current_ip,
                )
        except KeyboardInterrupt: #user requested shutdown
            log.info(
                "DuckDNS IP monitor stopped."
            )
            break
        except Exception as error:
            log.error(
                "Unexpected error: %s",
                error,
            )
        try:
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            log.info(
                "DuckDNS IP monitor stopped."
            )
            break
if __name__ == "__main__":
    main()
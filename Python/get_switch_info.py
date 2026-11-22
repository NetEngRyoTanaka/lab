import csv
import getpass
import os
import re

from netmiko import ConnectHandler

SWITCHES = ["10.255.128.21", "10.255.128.133", "10.255.128.202"]
USERNAME = "admin"
DEVICE_TYPE = "cisco_ios"
# change for other vendors (e.g. arista_eos, juniper_junos)


def get_password():
    """Read the password from an environment variable, or prompt for it."""
    return os.environ.get("SWITCH_PASSWORD") or getpass.getpass("Switch password: ")


def parse_version(output):
    match = re.search(r"Version\s+([^\s,]+)", output)
    return match.group(1) if match else "NOT FOUND"


def parse_serial(output):
    match = re.search(r"Processor board ID\s+(\S+)", output)
    return match.group(1) if match else "NOT FOUND"


def collect(host, password):
    device = {
        "device_type": DEVICE_TYPE,
        "host": host,
        "username": USERNAME,
        "password": password,
        "timeout": 20,
    }
    with ConnectHandler(**device) as conn:
        output = conn.send_command("show version")   # change command for other vendors
    return {
        "host": host,
        "version": parse_version(output),
        "serial": parse_serial(output),
        "status": "OK",
    }


def main():
    password = get_password()
    results = []

    for host in SWITCHES:
        try:
            results.append(collect(host, password))
            print(f"[OK]   {host}")
        except Exception as err:
            # One bad switch should not stop the whole run
            print(f"[FAIL] {host}: {err}")
            results.append({"host": host, "version": "", "serial": "", "status": f"FAILED: {err}"})

    with open("switch_inventory.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["host", "version", "serial", "status"])
        writer.writeheader()
        writer.writerows(results)

    print("\nSaved to switch_inventory.csv")


if __name__ == "__main__":
    main()

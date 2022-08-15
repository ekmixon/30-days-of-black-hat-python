# for creating network packets 

import queue
import scapy.all as scapy
# for matching regex expressions 
import re
import socket
from threading import Thread,Lock
from queue import Queue

# Arp ping scan Code ! 
def arp_ping(ip):
        # code for validating the ip address range syntax 
        if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]*$',ip):
            print("[-] Please provide a valid Ip address range for arp ping !")
            exit(1)
            
            
        try:
            arp_request_frame=scapy.ARP(pdst=ip) # creating a arp request frame with ip destination to our range provided !
            
            ether_broadcast_frame=scapy.Ether(dst="ff:ff:ff:ff:ff:ff") # setting the broadcast mac address to broadcast address ! 
            
            broadcast_arp_packet=ether_broadcast_frame/arp_request_frame # combining layer 2 and layer3 packets together ! means we have combined ethernet and arp frame togther ! 
            
            active_clients=scapy.srp(broadcast_arp_packet,timeout=3,verbose=False)[0] 
            #.srp function takes the whole packet and transmits and also we are storing the response in the active_clients variable !
            # In response we are returned a tuple  of length 2 in which clients who replied are in index 0 and who didn't replied are index 1 so we are only gathering active clients 
            print("""----------------------------------\nIPaddress\tMac address\n----------------------------------""")
            # Printing the result 
            

            # .psrc => Source Ip address
            # .hwsrc=>destination mac address
            # In reply of active replied clients we are replied with a list in which the first index '0' consists the data about 2nd layer The Data Link layer and in index 1 it consists the data about Network layer so are parsing data from the layer 3 
            # The index 1 has a object inside it which has data , we are only taking psrc and hwsrc ! 
            for i in range(0,len(active_clients)):
                print(f"{active_clients[i][1].psrc}\t{active_clients[i][1].hwsrc}")
            print("\n\n")
        except Exception as err:
            # Capturing the error !
            print(f"[-] Error occured !, Reason => {err}")
    
    
# Threaded Port scanner Code ! 

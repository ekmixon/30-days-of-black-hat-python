import scans
# for unconditionally terminating the program ! 
from sys import exit
from threading import Lock,Thread
from queue import Queue
# for creating command-line arguments
import socket
import argparse
import re
# Creating command-line arguments ! 
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('ip',help="Target IP address/range")
    parser.add_argument('-arp',dest='arp',help="Use this for arp ping!",required=False,action='store_true')
    parser.add_argument('-pT',dest="tcpPortScan",help="Tcp Port Scan",required=False,action='store_true')
    parser.add_argument('-pu',dest="UdpPortScan",help="Udp Port Scan",required=False,action='store_true')
    parser.add_argument('-p',dest="ports",help="ports to scan e.g. 80-443",required=False,action='store')
    
    arguments=parser.parse_args()
    
    if  arguments.tcpPortScan:
       if not arguments.ports:
           print("[-] Please specify port the ports in the desired manner e.g. 80-443")
           exit()   
    if not arguments.ip  :
        print("[-] Please Provide a valid Ip address or a IP address range! ")
        
   # Returning the arguments ! 
    return arguments
def tcp_threads():
    global q
    q=Queue()
    threads=200
    print_lock=Lock()
    
    
    
    
def tcp_port_open(ip,port):
    try:
        # creating the socket object !
        client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client.settimeout(1)
        # Connecting to host at a specific port ! 
        client.connect((ip,port))
    except socket.gaierror:
        print ('Hostname could not be resolved. Exiting')
    except KeyboardInterrupt:
         print ('You pressed Ctrl+C')
         exit(1)
    except:
        return False
    else:
        return True
    
    
def tcp_port_scan(ip,start_port,end_port):
    if not re.match(r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$',ip):
        print("[-] Please provide a valid Ip address for Tcp Port Scan!")
        exit()
    open_ports=[]
    for port in range(start_port,end_port):
        if tcp_port_open(ip,port=port):
            open_ports.append(port)
    if open_ports:
        print("""-----------------------\nPort\tState\n-----------------------""")
        for openPort in open_ports:
            print(f"{openPort}\tOpen")

if __name__=="__main__":
    # parsing the arguments
    arguments=get_args()
    q=Queue()
    lock=Lock()
    # parsing the ports !
    start_port,end_port=arguments.ports.split('-')
    # For arp Scan ! 
    if arguments.arp:
        print("\n----------------------------------------\n\tArp Ping Scan Results \n-----------------------------------------")
        scans.arp_ping(arguments.ip)
    # For Tcp port Scan ! 
    if arguments.tcpPortScan:
        print("\n-------------------------TCP Port Scan going on-------------------------")
        scans.tcp_port_scan(arguments.ip,int(start_port),int(end_port))
    